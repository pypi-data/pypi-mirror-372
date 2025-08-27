# import libs
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class stdioMCP(BaseModel):
    """
    Model for standard input/output MCP configuration.
    """
    transport: str = Field("stdio", description="Transport method for the MCP")
    command: Optional[str] = Field(None, description="Command to run the MCP")
    args: List[str] = Field(
        default_factory=list,
        description="Arguments for the command"
    )
    env: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Environment variables for the command"
    )


class streamableHttpMCP(BaseModel):
    """
    Model for streamable HTTP MCP configuration.
    """
    transport: str = Field(
        "streamable_http",
        description="Transport method for the MCP"
    )
    url: str = Field(..., description="URL for the MCP")
    env: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Environment variables for the HTTP MCP"
    )


MCP = Dict[str, str] | Dict[str, str | Dict[str, str]
                            ] | Dict[str, str | List[str] | Dict[str, str]]
