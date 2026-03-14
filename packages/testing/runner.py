from __future__ import annotations

from packages.evaluation import EvaluationInput, Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.observability.logging import get_logger
from packages.observability.tracing import span
from packages.prompt_registry import PromptService
from packages.testing.assertions import run_assertions
from packages.testing.models import AITestCase, AITestResult, AISuiteResult

logger = get_logger(__name__)


class AITestRunner:
    """
    Lightweight suite runner for AI API reliability checks.

    This runner intentionally stays simple:
    - resolve prompt from registry
    - generate via gateway
    - meter cost
    - evaluate output
    - apply assertion checks
    """

    def __init__(
        self,
        *,
        prompt_service: PromptService,
        model_gateway: ModelGateway,
        meter: CostMeter,
        evaluator: Evaluator,
    ) -> None:
        self.prompt_service = prompt_service
        self.model_gateway = model_gateway
        self.meter = meter
        self.evaluator = evaluator

    def run_case(self, case: AITestCase) -> AITestResult:
        logger.info(
            "ai_test_case_started",
            extra={
                "test_name": case.name,
                "prompt_name": case.prompt_name,
                "prompt_version": case.prompt_version,
                "model": case.model,
            },
        )

        with span(
            "test_prompt_render",
            test_name=case.name,
            prompt_name=case.prompt_name,
            prompt_version=case.prompt_version,
        ) as sp:
            rendered = self.prompt_service.render(
                name=case.prompt_name,
                version=case.prompt_version,
                variables=case.variables,
            )
            sp.set_attributes(
                prompt_hash=rendered.hash,
                resolved_prompt_version=rendered.version,
            )

        with span(
            "test_model_generate",
            test_name=case.name,
            requested_model=case.model,
        ) as sp:
            model_response = self.model_gateway.generate(
                model=case.model,
                prompt=rendered.content,
                max_tokens=case.max_tokens,
            )
            sp.set_attributes(
                provider=model_response.provider,
                resolved_model=model_response.model,
                input_tokens=model_response.usage.input_tokens,
                output_tokens=model_response.usage.output_tokens,
                total_tokens=model_response.usage.total_tokens,
            )

        with span(
            "test_cost_metering",
            test_name=case.name,
            provider=model_response.provider,
            resolved_model=model_response.model,
        ) as sp:
            cost_record = self.meter.record(
                model=model_response.model,
                usage=model_response.usage,
            )
            sp.set_attributes(
                total_cost_usd=str(cost_record.total_cost_usd),
            )

        with span(
            "test_evaluation",
            test_name=case.name,
            provider=model_response.provider,
            resolved_model=model_response.model,
        ) as sp:
            evaluation = self.evaluator.evaluate(
                EvaluationInput(
                    prompt=rendered.content,
                    response=model_response.content,
                    required_terms=case.expected_contains,
                    max_response_chars=case.max_response_chars,
                )
            )
            sp.set_attributes(
                evaluation_status=evaluation.status,
                reliability_score=evaluation.reliability_score,
            )

        assertions_passed, assertion_details = run_assertions(
            content=model_response.content,
            expected_contains=case.expected_contains,
            max_response_chars=case.max_response_chars,
        )

        passed = evaluation.status == "pass" and assertions_passed

        details = {
            "prompt_hash": rendered.hash,
            "source_request_id": case.source_request_id,
            "assertions": assertion_details,
        }

        result = AITestResult(
            test_name=case.name,
            passed=passed,
            provider=model_response.provider,
            model=model_response.model,
            prompt_name=rendered.name,
            prompt_version=rendered.version,
            trace_id=None,
            cost=cost_record.as_dict(),
            evaluation=evaluation.as_dict(),
            details=details,
        )

        logger.info(
            "ai_test_case_finished",
            extra={
                "test_name": case.name,
                "passed": passed,
                "provider": model_response.provider,
                "model": model_response.model,
            },
        )

        return result

    def run_suite(
        self,
        *,
        suite_name: str,
        cases: list[AITestCase],
    ) -> AISuiteResult:
        results = [self.run_case(case) for case in cases]
        passed_cases = sum(1 for result in results if result.passed)
        failed_cases = len(results) - passed_cases

        logger.info(
            "ai_test_suite_finished",
            extra={
                "suite_name": suite_name,
                "total_cases": len(results),
                "passed_cases": passed_cases,
                "failed_cases": failed_cases,
            },
        )

        return AISuiteResult(
            suite_name=suite_name,
            total_cases=len(results),
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            results=results,
        )
