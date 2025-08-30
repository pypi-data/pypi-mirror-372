"""
Dashgram SDK Enums Module.

This module contains enumerations used throughout the Dashgram SDK,
primarily for defining Telegram update types and event handlers.
"""

from enum import Enum


class HandlerType(Enum):
    """
    Enumeration of all supported Telegram update types.
    
    This enum defines all the different types of Telegram updates that can be
    tracked by the Dashgram SDK. Each value corresponds to a specific Telegram
    Bot API update type.
    """
    
    MESSAGE = "message"
    EDITED_MESSAGE = "edited_message"
    CHANNEL_POST = "channel_post"
    EDITED_CHANNEL_POST = "edited_channel_post"
    BUSINESS_CONNECTION = "business_connection"
    BUSINESS_MESSAGE = "business_message"
    EDITED_BUSINESS_MESSAGE = "edited_business_message"
    DELETED_BUSINESS_MESSAGES = "deleted_business_messages"
    MESSAGE_REACTION = "message_reaction"
    MESSAGE_REACTION_COUNT = "message_reaction_count"
    INLINE_QUERY = "inline_query"
    CHOSEN_INLINE_RESULT = "chosen_inline_result"
    CALLBACK_QUERY = "callback_query"
    SHIPPING_QUERY = "shipping_query"
    PRE_CHECKOUT_QUERY = "pre_checkout_query"
    PURCHASED_PAID_MEDIA = "purchased_paid_media"
    POLL = "poll"
    POLL_ANSWER = "poll_answer"
    MY_CHAT_MEMBER = "my_chat_member"
    CHAT_MEMBER = "chat_member"
    CHAT_JOIN_REQUEST = "chat_join_request"
    CHAT_BOOST = "chat_boost"
    REMOVED_CHAT_BOOST = "removed_chat_boost"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def all_types(cls) -> list[str]:
        """
        Get a list of all handler type values.
        
        Returns:
            A list containing all the string values of the HandlerType enum.
        
        Example:
            >>> HandlerType.all_types()
            ['message', 'edited_message', 'channel_post', ...]
        """
        return [e.value for e in cls]
