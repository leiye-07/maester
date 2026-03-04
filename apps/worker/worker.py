"""
Async worker service.

Responsibilities:
- document ingestion jobs
- chunking + embedding pipelines
- background maintenance tasks

Future queue tasks:
- document_parse
- document_chunk
- embedding_generation
- vector_index_update

Queue backend:
- Redis
- ARQ or Celery (to be decided)
"""