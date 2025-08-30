"""
Dashgram SDK for Python.

A comprehensive Python SDK for tracking and analyzing Telegram bot events
with seamless integration for popular Python Telegram bot frameworks.

This package provides:
- Easy integration with aiogram, python-telegram-bot, and pyTelegramBotAPI
- Automatic event tracking and analytics
- Support for all Telegram update types
- Robust error handling and configuration options

Quick Start:
    >>> from dashgram import Dashgram, HandlerType
    >>> sdk = Dashgram(project_id="123", access_key="your_key")
    >>> await sdk.track_event(event_data, HandlerType.MESSAGE)

Framework Integration:
    >>> # aiogram
    >>> sdk.bind_aiogram(dp)
    
    >>> # python-telegram-bot
    >>> sdk.bind_telegram(application)
    
    >>> # pyTelegramBotAPI
    >>> sdk.bind_telebot(bot)

For more information, visit: https://docs.dashgram.io
"""

from .client import Dashgram
from .enums import HandlerType


__all__ = ["Dashgram", "HandlerType"]

__version__ = "0.1.0"
