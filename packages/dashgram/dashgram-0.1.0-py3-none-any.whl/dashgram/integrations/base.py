"""
Dashgram SDK Base Integration Module.

This module provides base functionality for framework detection and object
conversion across different Telegram bot frameworks. It automatically
detects which framework is being used and routes object conversion
to the appropriate framework-specific module.
"""

import typing

from dashgram.integrations import aiogram, telegram, telebot
from dashgram.enums import HandlerType

# Mapping of framework names to their object conversion functions
_MAPPING = {
    "aiogram": aiogram.object_to_dict,
    "telegram": telegram.object_to_dict,
    "telebot": telebot.object_to_dict,
}


def get_package(obj) -> typing.Optional[str]:
    """
    Extract the package name from an object's module.
    
    This function analyzes an object's module path to determine which
    framework package it belongs to (aiogram, telegram, telebot, etc.).
    
    Args:
        obj: The object to analyze
    
    Returns:
        The package name if recognized, None otherwise
    
    Example:
        >>> from aiogram.types import Message
        >>> message = Message()
        >>> get_package(message)
        'aiogram'
    """
    package = obj.__module__.split(".")[0]
    if package not in _MAPPING:
        return None
    return package


def determine_object_source(obj):
    """
    Determine the appropriate conversion function for an object.
    
    This function identifies which framework an object belongs to and
    returns the corresponding object conversion function.
    
    Args:
        obj: The object to analyze
    
    Returns:
        The appropriate conversion function or None if not supported
    
    Example:
        >>> from aiogram.types import Message
        >>> message = Message()
        >>> conv_func = determine_object_source(message)
        >>> # conv_func will be aiogram.object_to_dict
    """
    package = get_package(obj)
    if package is None:
        return None
    return _MAPPING[package]


def object_to_dict(obj, handler_type: typing.Optional[HandlerType] = None):
    """
    Convert a framework object to a dictionary format for the Dashgram API.
    
    This function automatically detects the framework of the input object
    and uses the appropriate conversion function to transform it into
    a dictionary format that can be sent to the Dashgram API.
    
    Args:
        obj: The framework object to convert (aiogram, telegram, or telebot)
        handler_type: The type of handler (optional, used for validation)
    
    Returns:
        A dictionary representation of the object, or empty dict if conversion fails
    
    Example:
        >>> from aiogram.types import Message
        >>> message = Message()
        >>> result = object_to_dict(message, HandlerType.MESSAGE)
        >>> # result will be a dictionary representation of the update
    """
    conv = determine_object_source(obj)
    if conv is None:
        return {}

    return conv(obj, handler_type)


def resolve_framework() -> typing.Optional[str]:
    """
    Automatically detect which Telegram bot framework is being used.
    
    This function checks which framework packages are installed and
    returns the name of the detected framework. It's used to set
    the origin string for tracking.
    
    Returns:
        The name of the detected framework ("Aiogram", "python-telegram-bot",
        "pyTelegramBotAPI") or None if no framework is detected
    
    Example:
        >>> framework = resolve_framework()
        >>> if framework:
        ...     print(f"Detected framework: {framework}")
        ... else:
        ...     print("No supported framework detected")
    """
    if aiogram.aiogram:
        return "Aiogram"
    if telegram.telegram:
        return "python-telegram-bot"
    if telebot.telebot:
        return "pyTelegramBotAPI"
    return None
