from typing import Dict, Union, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class AppInfo(BaseModel):
    name: str = Field(..., description="App name.")
    version: Union[str, None] = Field(None, description="App version.")
    description: Union[str, None] = Field(None, description="App description.")


class AgentDetails(BaseModel):
    exists: bool = Field(..., description="Agent exists.")
    model_provider: str = Field(..., description="Model provider.")
    model_name: str = Field(..., description="Model name.")
    agent_name: str = Field(..., description="Agent name.")
    agent_prompt: str = Field(..., description="Agent prompt.")
    mcp_source: Optional[
        Union[
            Dict[str, Dict[str, str]],
            Dict[str, Dict[str, str] | Dict[str, str]],
            Dict[str, Dict[str, str | List[str] | Dict[str, str]]],
            str,
            Path
        ]
    ] = Field(
        None, description="MCP configurations or path to YAML file.")
    memory_mode: bool = Field(
        False, description="Enable memory mode for the agent.")


class LlmDetails(BaseModel):
    temperature: float = Field(..., description="LLM temperature.")
    max_tokens: int = Field(..., description="LLM max tokens.")


class OverallSettings(BaseModel):
    cors_origins: Union[List[str], None] = Field(
        None,
        description="Allowed CORS origins."
    )


class ApiConfigSummary(BaseModel):
    app: AppInfo
    agent: List[AgentDetails]
    llm: LlmDetails
    settings: OverallSettings
