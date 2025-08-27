# import libs
from typing import Dict, Union, List, Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    model_provider: Optional[str] = Field(
        default=None,
        description="Provider of the LLM model (e.g., 'openai', 'google')"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Name of the LLM model to use"
    )
    agent_name: Optional[str] = Field(
        default=None,
        description="Name of the agent"
    )
    agent_prompt: Optional[str] = Field(
        default=None,
        description="Prompt for the agent"
    )
    mcp_source: Optional[
        Union[
            Dict[str, Dict[str, str]],
            Dict[str, Dict[str, str] | Dict[str, str]],
            Dict[str, Dict[str, str | List[str] | Dict[str, str]]],
        ]
    ] = Field(
        default=None,
        description="Source for the MCP data"
    )
    memory_mode: Optional[bool] = Field(
        default=False,
        description="Enable or disable memory mode"
    )


class LlmConfig(BaseModel):
    model_provider: str = Field(
        default="openai",
        description="Provider of the LLM model (e.g., 'openai', 'google')"
    )
    model_name: str = Field(
        default="gpt-4-mini",
        description="Name of the LLM model to use"
    )
    temperature: float = Field(
        default=0.0,
        description="Temperature for the LLM model"
    )
    max_tokens: int = Field(
        default=2048,
        description="Maximum number of tokens for the LLM model"
    )
