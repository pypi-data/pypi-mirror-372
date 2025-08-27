import structlog
from fastapi import HTTPException, status

from langgate.registry import ModelRegistry
from langgate.registry.models import ImageModelInfo, LLMInfo

logger = structlog.stdlib.get_logger(__name__)


class ModelRegistryAPI:
    """
    API for accessing the model registry.
    This will be expanded when gateway becomes a microservice.
    """

    def __init__(self, registry: ModelRegistry | None = None):
        self.registry = registry or ModelRegistry()

    async def get_llm_info(self, model_id: str) -> LLMInfo:
        """Get LLM information."""
        try:
            return self.registry.get_llm_info(model_id)
        except ValueError as exc:
            if "not found" in str(exc):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model {model_id} not found",
                ) from exc
            await logger.aexception("model_info_error", model_id=model_id)
            raise

    async def list_llms(self) -> list[LLMInfo]:
        """List all available LLMs."""
        return self.registry.list_llms()

    async def get_image_model_info(self, model_id: str) -> ImageModelInfo:
        """Get image model information."""
        try:
            return self.registry.get_image_model_info(model_id)
        except ValueError as exc:
            if "not found" in str(exc):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model {model_id} not found",
                ) from exc
            await logger.aexception("model_info_error", model_id=model_id)
            raise

    async def list_image_models(self) -> list[ImageModelInfo]:
        """List all available image models."""
        return self.registry.list_image_models()
