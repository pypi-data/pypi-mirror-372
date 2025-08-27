# import libs
import logging
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
# local imports
from ..llms import LlmManager
from ..config import llm_providers, default_model_settings
from ..models import LlmConfig

# NOTE: logger
logger = logging.getLogger(__name__)

# NOTE: llm parameters
# set default values for model provider and name
DEFAULT_TEMPERATURE = default_model_settings['temperature']
DEFAULT_MAX_TOKENS = default_model_settings['max_tokens']

# SECTION: api router
llm_router = APIRouter(prefix="/llm")

# SECTION: routes


@llm_router.post("/ping", response_model=bool)
async def ping_request(
    request: Request
):
    """
    Ping the LLM to check if it is running.

    Parameters
    ----------
    request : LlmConfig
        Configuration for the LLM, including:
    - model_provider: str
        The provider of the LLM model (e.g., "openai", "google").
    - model_name: str
        The name of the LLM model to use (e.g., "gpt-3.5-turbo", "gemini-1.5-pro").
    - temperature: float
        The temperature for the LLM model, controlling randomness in responses.
    - max_tokens: int
        The maximum number of tokens for the LLM model response.
    """
    try:
        # SECTION: Request parameters
        # NOTE: extract app
        app = request.app

        # SECTION: extract parameters
        # check if app state has the required attributes
        if not hasattr(app.state, "model_provider") or not hasattr(app.state, "model_name"):
            raise HTTPException(
                status_code=400, detail="Model provider and name must be set in app state.")
        # extract parameters from app state
        # NOTE: model provider and name
        if not hasattr(app.state, "temperature"):
            app.state.temperature = DEFAULT_TEMPERATURE
        if not hasattr(app.state, "max_tokens"):
            app.state.max_tokens = DEFAULT_MAX_TOKENS

        # extract parameters from app state
        # NOTE: model provider and name
        model_provider = app.state.model_provider
        model_name = app.state.model_name
        temperature = app.state.temperature
        max_tokens = app.state.max_tokens

        logger.info(
            f"Initializing LLM with provider: {model_provider}, model: {model_name}, temperature: {temperature}, max_tokens: {max_tokens}")

        # NOTE: add kwargs for LLM manager
        kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # SECTION: validate inputs
        if not model_provider or not model_name:
            raise HTTPException(
                status_code=400, detail="Model provider and name must be provided.")

        # NOTE: check if model provider is supported
        if model_provider not in llm_providers:
            raise HTTPException(
                status_code=400, detail=f"Unsupported model provider: {model_provider}. Supported providers are: {', '.join(llm_providers)}.")

        # SECTION: init llm manager
        llm_manager = LlmManager(
            model_provider=model_provider,
            model_name=model_name,
            **kwargs
        )

        # SECTION: ping the model
        response = llm_manager.ping()

        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@llm_router.post("/ping-me", response_model=bool)
async def ping_llm(
    request: LlmConfig
):
    """
    Ping the LLM to check if it is running based on the provided configuration.

    Parameters
    ----------
    request : LlmConfig
        Configuration for the LLM, including:
    - model_provider: str
        The provider of the LLM model (e.g., "openai", "google").
    - model_name: str
        The name of the LLM model to use (e.g., "gpt-3.5-turbo", "gemini-1.5-pro").
    - temperature: float
        The temperature for the LLM model, controlling randomness in responses.
    - max_tokens: int
        The maximum number of tokens for the LLM model response.
    """
    try:
        # SECTION: extract parameters
        model_provider = request.model_provider
        model_name = request.model_name
        temperature = request.temperature
        max_tokens = request.max_tokens

        logger.info(
            f"Initializing LLM with provider: {model_provider}, model: {model_name}, temperature: {temperature}, max_tokens: {max_tokens}")

        # NOTE: add kwargs for LLM manager
        kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # SECTION: validate inputs
        if not model_provider or not model_name:
            raise HTTPException(
                status_code=400, detail="Model provider and name must be provided.")

        # NOTE: check if model provider is supported
        if model_provider not in llm_providers:
            raise HTTPException(
                status_code=400, detail=f"Unsupported model provider: {model_provider}. Supported providers are: {', '.join(llm_providers)}.")

        # SECTION: init llm manager
        llm_manager = LlmManager(
            model_provider=model_provider,
            model_name=model_name
        )

        # SECTION: ping the model
        response = llm_manager.ping()

        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))
