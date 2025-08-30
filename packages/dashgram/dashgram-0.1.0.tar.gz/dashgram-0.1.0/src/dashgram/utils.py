"""
Dashgram SDK Utilities Module.

This module contains utility functions and decorators used throughout
the Dashgram SDK for common operations like async/sync conversion
and event formatting.
"""

import functools
import asyncio
import typing

from dashgram.enums import HandlerType


def auto_async(func):
    """
    Decorator to automatically handle async/sync function calls.
    
    This decorator allows async functions to be called from both async and sync
    contexts. If called from an async context, it returns the coroutine directly.
    If called from a sync context, it creates a new event loop and runs the
    coroutine to completion.
    
    Args:
        func: The async function to decorate
    
    Returns:
        A wrapper function that handles both async and sync contexts
    
    Example:
        >>> @auto_async
        ... async def my_async_function():
        ...     return "Hello from async!"
        
        >>> # Can be called from async context
        >>> result = await my_async_function()
        
        >>> # Can also be called from sync context
        >>> result = my_async_function()  # Automatically runs to completion
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        coro = func(*args, **kwargs)
        try:
            loop = asyncio.get_running_loop()
            return coro
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
    return wrapper


def wrap_event(event: dict, handler_type: typing.Optional[HandlerType] = None) -> dict:
    """
    Wrap a raw event dictionary in the proper format for the Dashgram API.
    
    This function takes a raw event dictionary and wraps it in the format
    expected by the Dashgram API. If the event already has an update_id or
    no handler_type is provided, it returns the event as-is.
    
    Args:
        event: The raw event dictionary to wrap
        handler_type: The type of handler for this event (optional)
    
    Returns:
        A properly formatted event dictionary for the Dashgram API
    
    Example:
        >>> # Wrap a simple message event
        >>> event = {"text": "Hello, world!"}
        >>> wrapped = wrap_event(event, HandlerType.MESSAGE)
        >>> print(wrapped)
        {'update_id': -1, 'message': {'text': 'Hello, world!'}}
        
        >>> # Event with existing update_id is returned as-is
        >>> event = {"update_id": 123, "message": {"text": "Hello"}}
        >>> wrapped = wrap_event(event)
        >>> print(wrapped)
        {'update_id': 123, 'message': {'text': 'Hello'}}
    """
    if event.get("update_id") is not None or handler_type is None:
        return event
    return {"update_id": -1, **{str(handler_type): event}}
