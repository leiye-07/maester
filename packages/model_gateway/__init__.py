## Responsibilities of the gateway
# - accept provider-agnostic generation requests
# - route requests to the correct provider
# - apply fallback policy when needed
# - isolate provider adapters from application code

## Current gateway structure
# - `base.py` defines the provider contract
# - `provider_openai.py` implements an OpenAI-style adapter
# - `provider_anthropic.py` implements an Anthropic-style adapter
# - `router.py` selects providers and applies fallback rules
# - `client.py` exposes a simple gateway interface to the rest of the system

from packages.model_gateway.client import ModelGateway
from packages.model_gateway.base import GenerationRequest, GenerationResponse

__all__ = [
    "ModelGateway",
    "GenerationRequest",
    "GenerationResponse",
]