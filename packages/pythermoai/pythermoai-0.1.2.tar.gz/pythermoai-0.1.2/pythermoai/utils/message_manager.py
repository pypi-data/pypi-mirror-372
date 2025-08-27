# import libs
import logging
from fastapi import HTTPException
from typing import Union, List
from langchain_core.messages import (
    ToolMessage, AIMessage, HumanMessage, SystemMessage
)
# local
from ..models import AgentMessage, TokenMetadata

# NOTE: logger
logger = logging.getLogger(__name__)


def agent_message_analyzer(
    message: Union[
        ToolMessage,
        AIMessage,
        HumanMessage,
        SystemMessage
    ],
    ignore_messages: List[str] = ['HumanMessage', 'SystemMessage']
) -> AgentMessage | None:
    """
    Analyzes a list of messages and returns a summary of the content.

    Parameters
    ----------
    message : Union[ToolMessage, AIMessage, HumanMessage, SystemMessage]
        A message object from the LangChain library, which can be of type ToolMessage, AIMessage,
        HumanMessage, or SystemMessage.
    ignore_messages : List[str], optional
        A list of message types to ignore during analysis. Default is ['HumanMessage', 'SystemMessage'].
    """
    try:
        # SECTION: ignore message types
        message_type = type(message).__name__
        if message_type in ignore_messages:
            return None

        # SECTION: validate message type
        if not isinstance(
            message,
            (
                ToolMessage,
                AIMessage,
                HumanMessage,
                SystemMessage
            )
        ):
            logger.error(f"Invalid message type: {type(message)}")

        # SECTION: extract data from message **response_metadata**
        # NOTE: set input_tokens and output_tokens
        if hasattr(message, 'response_metadata'):
            response_metadata = message.response_metadata
            output_tokens = getattr(response_metadata, 'output_tokens', 0)
            input_tokens = getattr(response_metadata, 'input_tokens', 0)
        else:
            output_tokens = -1
            input_tokens = -1

        # SECTION: analyze message content
        # NOTE: iterate through messages
        if isinstance(message, ToolMessage):
            # tool message
            return AgentMessage(
                type="tool",
                content=message.content,
                tool_calls=None,
                name=message.name,
                tool_call_id=message.tool_call_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        elif isinstance(message, AIMessage):
            # NOTE: AIMessage can contain tool calls
            # tool calls message or assistant message
            return AgentMessage(
                type="assistant",
                content=message.content,
                tool_calls=message.tool_calls if hasattr(
                    message, 'tool_calls') else None,
                name=message.name if hasattr(message, 'name') else None,
                tool_call_id=None,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

        elif isinstance(message, HumanMessage):
            # human message
            return AgentMessage(
                type="user",
                content=message.content,
                tool_calls=None,
                name=message.name if hasattr(message, 'name') else None,
                tool_call_id=None,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

        elif isinstance(message, SystemMessage):
            # system message
            return AgentMessage(
                type="system",
                content=message.content,
                tool_calls=None,
                name=message.name if hasattr(message, 'name') else None,
                tool_call_id=None,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        else:
            return AgentMessage(
                type="unknown",
                content=message.content if hasattr(message, 'content') else "",
                tool_calls=None,
                name=None,
                tool_call_id=None,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

    except Exception as e:
        logger.error(f"Error analyzing messages: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to analyze messages") from e


def message_token_counter(
    message: Union[ToolMessage, AIMessage, HumanMessage, SystemMessage]
) -> TokenMetadata:
    """
    Counts the tokens in a message and returns an AgentMessage with token counts.

    Parameters
    ----------
    message : Union[ToolMessage, AIMessage, HumanMessage, SystemMessage]
        A message object from the LangChain library.

    Returns
    -------
    AgentMessage
        An AgentMessage containing the token counts.
    """
    try:
        # SECTION: analyze message content
        agent_message = agent_message_analyzer(message)

        if agent_message is None:
            raise HTTPException(
                status_code=400, detail="Invalid message type or content"
            )

        # SECTION: create TokenMetadata
        # NOTE: access to usage_metadata
        if isinstance(message, AIMessage):
            # get response metadata to check for usage metadata
            if hasattr(message, 'usage_metadata'):
                usage_metadata = message.usage_metadata
            else:
                usage_metadata = None

        # check
        if usage_metadata is not None:
            input_tokens = usage_metadata.get('input_tokens', -1)
            output_tokens = usage_metadata.get('output_tokens', -1)

            # set token metadata
            token_metadata = TokenMetadata(
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        else:
            token_metadata = TokenMetadata(
                input_tokens=-1,
                output_tokens=-1
            )

        return token_metadata
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to count tokens") from e
