# import libs
import logging
from typing import (
    Dict,
    Union,
    Any
)
from pathlib import Path
# local
from ..models import stdioMCP, streamableHttpMCP
from ..utils import load_yaml_file

# NOTE: logger
logger = logging.getLogger(__name__)


class MCPManager:
    '''
    MCPManager class for managing MCP configurations.
    '''

    def __init__(self, mcp: dict | str | Path):
        '''
        Initialize the MCPManager with a configuration.

        Parameters
        ----------
        mcp : dict
            The configuration dictionary for the MCPs.
        '''
        # NOTE: set attributes
        self.mcp = mcp

    def _load_mcp_from_yaml(
        self,
        mcp_source: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Load MCP configurations from a YAML file.

        Parameters
        ----------
        mcp_source : str or Path
            The path to the YAML file containing MCP configurations.

        Returns
        -------
        dict
            A dictionary containing the MCP configurations.
        """
        try:
            return load_yaml_file(mcp_source)
        except Exception as e:
            logger.error(
                f"Failed to load MCP configurations from {mcp_source}: {e}")
            raise RuntimeError(
                f"Failed to load MCP configurations: {e}") from e

    def config_mcp(
        self
    ) -> Dict[str, Union[stdioMCP, streamableHttpMCP]]:
        '''
        Configure and return the MCP configurations.

        Returns
        -------
        Dict[str, Union[stdioMCP, streamableHttpMCP]]
            A dictionary containing the MCP configurations.
        '''
        try:
            # SECTION: checking inputs
            # check if mcp is empty
            if not self.mcp:
                logger.warning("No MCP configurations provided.")
                return {}

            # check if mcp is a string or Path
            if isinstance(self.mcp, (str, Path)):
                # load MCP configurations from YAML file
                self.mcp = self._load_mcp_from_yaml(self.mcp)

            # SECTION: create MCP configurations
            # initialize an empty dictionary to hold MCP configurations
            mcp_dict = {}

            # iterate through the MCP configurations
            for mcp_name, mcp_config in self.mcp.items():
                if mcp_config['transport'] == 'stdio':
                    mcp_dict[mcp_name] = stdioMCP(**mcp_config)
                elif mcp_config['transport'] == 'streamable_http':
                    mcp_dict[mcp_name] = streamableHttpMCP(**mcp_config)
                else:
                    raise ValueError(
                        f"Unsupported transport type: {mcp_config['transport']}")
            return mcp_dict
        except Exception as e:
            logger.error(f"Failed to get MCP configurations: {e}")
            raise RuntimeError(f"Failed to get MCP configurations: {e}") from e
