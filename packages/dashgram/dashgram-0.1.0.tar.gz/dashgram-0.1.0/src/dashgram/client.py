"""
Dashgram SDK Client Module.

This module provides the main Dashgram client for tracking Telegram bot events
and integrating with popular Python Telegram bot frameworks.
"""

import typing
import httpx
import warnings

from dashgram.integrations.base import object_to_dict, resolve_framework
from dashgram.integrations import aiogram, telegram, telebot
from dashgram.enums import HandlerType
from dashgram.exceptions import InvalidCredentials, DashgramApiError
from dashgram.utils import auto_async, wrap_event


class Dashgram:
    """
    Main Dashgram SDK client for tracking Telegram bot events.
    
    This class provides methods to track events from Telegram bots and integrates
    seamlessly with popular Python Telegram bot frameworks like aiogram,
    python-telegram-bot, and pyTelegramBotAPI.
    
    Attributes:
        project_id: The Dashgram project identifier
        access_key: The authentication key for the Dashgram API
        api_url: The base URL for the Dashgram API
        origin: The origin string identifying the SDK and framework
    
    Example:
        >>> from dashgram import Dashgram
        >>> sdk = Dashgram(project_id="123", access_key="your_key")
        >>> await sdk.track_event(event_data)
    """
    
    def __init__(self, project_id: typing.Union[int, str], access_key: str, *,
                 api_url: typing.Optional[str] = None,
                 suppress_exceptions: bool = True,
                 origin: typing.Optional[str] = None) -> None:
        """
        Initialize the Dashgram client.
        
        Args:
            project_id: Your Dashgram project ID (can be int or string)
            access_key: Your Dashgram access key for authentication
            api_url: Custom API URL (defaults to https://api.dashgram.io/v1)
            origin: Custom origin string (auto-detected if not provided)
        
        Example:
            >>> sdk = Dashgram(
            ...     project_id="my_project",
            ...     access_key="my_access_key",
            ...     api_url="https://custom-api.com/v1"
            ... )
        """
        self.project_id = project_id
        self.access_key = access_key

        if api_url is None:
            api_url = "https://api.dashgram.io/v1"
        self.api_url = f"{api_url}/{project_id}"

        if origin is None:
            framework = resolve_framework()
            if framework is None:
                origin = "Python + Dashgram SDK"
            else:
                origin = f"Python + Dashgram SDK + {framework}"

        self.origin = origin
        
        self.suppress_exceptions = suppress_exceptions

        self._client = httpx.AsyncClient(base_url=self.api_url, headers={"Authorization": f"Bearer {access_key}"})

    async def _request(self, url: str, json: typing.Optional[typing.Dict[str, typing.Any]] = None, suppress_exceptions: typing.Optional[bool] = None) -> bool:
        """
        Make an HTTP request to the Dashgram API.
        
        Args:
            url: The endpoint URL to request
            json: JSON data to send with the request
            suppress_exceptions: Whether to suppress exceptions and return False instead
        
        Returns:
            True if the request was successful, False otherwise
        
        Raises:
            InvalidCredentials: If the API credentials are invalid
            DashgramApiError: If the API returns an error response
        """
        if suppress_exceptions is None:
            suppress_exceptions = self.suppress_exceptions

        try:
            resp = await self._client.post(url, json=json)
            
            if resp.status_code == 403:
                raise InvalidCredentials
            
            resp_data = resp.json()
            
            if resp.status_code != 200 or resp_data.get("status") != "success":
                raise DashgramApiError(resp.status_code, resp_data.get("details"))
            
            return True
        except Exception as e:
            if not suppress_exceptions:
                raise e
            warnings.warn(f"{type(e).__name__}: {e}")
            return False

    @auto_async
    async def track_event(self, event, handler_type: typing.Optional[HandlerType] = None, suppress_exceptions: typing.Optional[bool] = None) -> bool:
        """
        Track a Telegram event or update.
        
        This method can handle both framework objects (like aiogram Update) and
        raw dictionaries. It automatically converts framework objects to the
        proper format for the Dashgram API.
        
        Args:
            event: The event to track. Can be a framework object or dictionary
            handler_type: The type of handler (optional if event is a framework object)
            suppress_exceptions: Whether to suppress exceptions and return False
        
        Returns:
            True if the event was tracked successfully, False otherwise
        
        Raises:
            InvalidCredentials: If the API credentials are invalid
            DashgramApiError: If the API returns an error response
        
        Example:
            >>> # Track an aiogram update
            >>> await sdk.track_event(update)
            
            >>> # Track an aiogram message
            >>> await sdk.track_event(message, HandlerType.MESSAGE)
            
            >>> # Track a raw dictionary
            >>> await sdk.track_event({"text": "hello"}, HandlerType.MESSAGE)
            
            >>> # Track with exception handling
            >>> try:
            ...     await sdk.track_event(event, suppress_exceptions=False)
            ... except DashgramApiError as e:
            ...     print(f"API Error: {e.status_code}")
        """
        if not isinstance(event, dict):
            event = object_to_dict(event, handler_type)
        else:
            event = wrap_event(event, handler_type)

        req_data = {"origin": self.origin, "updates": [event]}

        return await self._request("track", json=req_data, suppress_exceptions=suppress_exceptions)
            
        
    @auto_async
    async def invited_by(self, user_id: int, invited_by: int, suppress_exceptions: typing.Optional[bool] = None) -> bool:
        """
        Track user invitation/referral.
        
        Use this method to track when one user invites another user to your bot
        or service. This is useful for referral programs and user analytics.
        
        Args:
            user_id: The ID of the invited user
            invited_by: The ID of the user who sent the invitation
            suppress_exceptions: Whether to suppress exceptions and return False
        
        Returns:
            True if the invitation was tracked successfully, False otherwise
        
        Raises:
            InvalidCredentials: If the API credentials are invalid
            DashgramApiError: If the API returns an error response
        
        Example:
            >>> # Track a user invitation
            >>> await sdk.invited_by(user_id=123456, invited_by=789012)
            
            >>> # Track with exception handling
            >>> success = await sdk.invited_by(
            ...     user_id=123456,
            ...     invited_by=789012,
            ...     suppress_exceptions=False
            ... )
        """
        req_data = {"user_id": user_id, "invited_by": invited_by, "origin": self.origin}
            
        return await self._request("invited_by", json=req_data, suppress_exceptions=suppress_exceptions)

    def bind_aiogram(self, dp) -> None:
        """
        Bind the SDK to an aiogram dispatcher for automatic event tracking.
        
        This method sets up automatic tracking for all events processed by the
        aiogram dispatcher. Once bound, all messages, callback queries, and other
        updates will be automatically tracked without manual intervention.
        
        Args:
            dp: The aiogram Dispatcher instance to bind to
        
        Example:
            >>> from aiogram import Bot, Dispatcher
            >>> from dashgram import Dashgram
            
            >>> dp = Dispatcher()
            >>> sdk = Dashgram(project_id="123", access_key="key")
            >>> sdk.bind_aiogram(dp)
            
            >>> # Now all events will be automatically tracked
            >>> @dp.message()
            >>> async def handle_message(message):
            ...     # This message will be automatically tracked
            ...     await message.answer("Hello!")
        """
        aiogram.bind(self, dp)

    def bind_telegram(self, app, group: int = -1, block: bool = False) -> None:
        """
        Bind the SDK to a python-telegram-bot application for automatic event tracking.
        
        This method sets up automatic tracking for all events processed by the
        python-telegram-bot application. Once bound, all updates will be
        automatically tracked without manual intervention.
        
        Args:
            app: The python-telegram-bot Application instance to bind to
            group: The handler group to use (default: -1)
            block: Whether handler shoulb be blocking (default: False)
        
        Example:
            >>> from telegram.ext import Application
            >>> from dashgram import Dashgram
            
            >>> application = Application.builder().token("TOKEN").build()
            >>> sdk = Dashgram(project_id="123", access_key="key")
            >>> sdk.bind_telegram(application)
            
            >>> # Now all events will be automatically tracked
            >>> async def handle_message(update, context):
            ...     # This update will be automatically tracked
            ...     await update.message.reply_text("Hello!")
        """
        telegram.bind(self, app, group, block)

    def bind_telebot(self, bot) -> None:
        """
        Bind the SDK to a pyTelegramBotAPI bot for automatic event tracking.
        
        This method sets up automatic tracking for all events processed by the
        pyTelegramBotAPI bot. Once bound, all messages, callback queries, and
        other updates will be automatically tracked without manual intervention.
        
        Args:
            bot: The pyTelegramBotAPI TeleBot or AsyncTeleBot instance to bind to
        
        Example:
            >>> import telebot
            >>> from dashgram import Dashgram
            
            >>> bot = telebot.TeleBot("TOKEN", use_class_middlewares=True)
            >>> sdk = Dashgram(project_id="123", access_key="key")
            >>> sdk.bind_telebot(bot)
            
            >>> # Now all events will be automatically tracked
            >>> @bot.message_handler(func=lambda message: True)
            >>> def handle_message(message):
            ...     # This message will be automatically tracked
            ...     bot.reply_to(message, "Hello!")
        """
        telebot.bind(self, bot)
