# deps.py
from fastapi import Depends, Request
from typing import Dict, Any
# local
from ..models import LlmConfig


def get_state(request: Request) -> Any:
    """Retrieve the application state from the request."""
    return request.app.state


def get_agents(state=Depends(get_state)) -> Dict[str, Any]:
    """Retrieve the agents dictionary from the application state."""
    # Ensure the dict exists
    if not hasattr(state, "agents"):
        state.agents = {}
    return state.agents


def get_llm_config_dep(state=Depends(get_state)):
    """Retrieve the LLM configuration from the application state."""
    return LlmConfig(
        model_provider=state.model_provider,
        model_name=state.model_name,
        temperature=state.temperature,
        max_tokens=state.max_tokens
    )


def get_mcp_source_dep(state=Depends(get_state)):
    """Retrieve the MCP source from the application state."""
    return state.mcp_source
