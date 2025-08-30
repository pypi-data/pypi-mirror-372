# pyTelegramBotAPI integration
import typing

from dashgram.enums import HandlerType

try:
    from telebot import TeleBot, types
    from telebot.async_telebot import AsyncTeleBot
    from telebot.handler_backends import BaseMiddleware
    from telebot.asyncio_handler_backends import BaseMiddleware as AsyncBaseMiddleware
    telebot = True
    
    class TrackMiddlewareMixin:
        def __init__(self, sdk):
            self.sdk = sdk

            self.update_sensitive = True
            self.update_types = HandlerType.all_types()


    class TrackMiddleware(TrackMiddlewareMixin, BaseMiddleware):
        def post_process_event(self, event_type: str, message, data, exception):
            try:
                handler_type = HandlerType[event_type.upper()]
                self.sdk.track_event(message, handler_type)
            except KeyError:
                pass

        def post_process_message(self, message, data, exception):
            self.post_process_event('message', message, data, exception)

        def post_process_callback_query(self, message, data, exception):
            self.post_process_event('callback_query', message, data, exception)

        def post_process_my_chat_member(self, message, data, exception):
            self.post_process_event('my_chat_member', message, data, exception)

        def post_process_edited_message(self, message, data, exception):
            self.post_process_event('edited_message', message, data, exception)

        def post_process_channel_post(self, message, data, exception):
            self.post_process_event('channel_post', message, data, exception)

        def post_process_edited_channel_post(self, message, data, exception):
            self.post_process_event('edited_channel_post', message, data, exception)

        def post_process_business_connection(self, message, data, exception):
            self.post_process_event('business_connection', message, data, exception)

        def post_process_business_message(self, message, data, exception):
            self.post_process_event('business_message', message, data, exception)

        def post_process_edited_business_message(self, message, data, exception):
            self.post_process_event('edited_business_message', message, data, exception)

        def post_process_deleted_business_messages(self, message, data, exception):
            self.post_process_event('deleted_business_messages', message, data, exception)

        def post_process_message_reaction(self, message, data, exception):
            self.post_process_event('message_reaction', message, data, exception)

        def post_process_message_reaction_count(self, message, data, exception):
            self.post_process_event('message_reaction_count', message, data, exception)

        def post_process_inline_query(self, message, data, exception):
            self.post_process_event('inline_query', message, data, exception)

        def post_process_chosen_inline_result(self, message, data, exception):
            self.post_process_event('chosen_inline_result', message, data, exception)

        def post_process_shipping_query(self, message, data, exception):
            self.post_process_event('shipping_query', message, data, exception)

        def post_process_pre_checkout_query(self, message, data, exception):
            self.post_process_event('pre_checkout_query', message, data, exception)

        def post_process_purchased_paid_media(self, message, data, exception):
            self.post_process_event('purchased_paid_media', message, data, exception)

        def post_process_poll(self, message, data, exception):
            self.post_process_event('poll', message, data, exception)

        def post_process_poll_answer(self, message, data, exception):
            self.post_process_event('poll_answer', message, data, exception)

        def post_process_chat_member(self, message, data, exception):
            self.post_process_event('chat_member', message, data, exception)

        def post_process_chat_join_request(self, message, data, exception):
            self.post_process_event('chat_join_request', message, data, exception)

        def post_process_chat_boost(self, message, data, exception):
            self.post_process_event('chat_boost', message, data, exception)

        def post_process_removed_chat_boost(self, message, data, exception):
            self.post_process_event('removed_chat_boost', message, data, exception)

        def pre_process_message(self, message, data):
            pass

        def pre_process_callback_query(self, message, data):
            pass

        def pre_process_my_chat_member(self, message, data):
            pass

        def pre_process_edited_message(self, message, data):
            pass

        def pre_process_channel_post(self, message, data):
            pass

        def pre_process_edited_channel_post(self, message, data):
            pass

        def pre_process_business_connection(self, message, data):
            pass

        def pre_process_business_message(self, message, data):
            pass

        def pre_process_edited_business_message(self, message, data):
            pass

        def pre_process_deleted_business_messages(self, message, data):
            pass

        def pre_process_message_reaction(self, message, data):
            pass

        def pre_process_message_reaction_count(self, message, data):
            pass

        def pre_process_inline_query(self, message, data):
            pass

        def pre_process_chosen_inline_result(self, message, data):
            pass

        def pre_process_shipping_query(self, message, data):
            pass

        def pre_process_pre_checkout_query(self, message, data):
            pass

        def pre_process_purchased_paid_media(self, message, data):
            pass

        def pre_process_poll(self, message, data):
            pass

        def pre_process_poll_answer(self, message, data):
            pass

        def pre_process_chat_member(self, message, data):
            pass

        def pre_process_chat_join_request(self, message, data):
            pass

        def pre_process_chat_boost(self, message, data):
            pass

        def pre_process_removed_chat_boost(self, message, data):
            pass


    class AsyncTrackMiddleware(TrackMiddlewareMixin, AsyncBaseMiddleware):
        async def post_process_event(self, event_type: str, message, data, exception):
            try:
                handler_type = HandlerType[event_type.upper()]
                await self.sdk.track_event(message, handler_type)
            except KeyError:
                pass

        async def post_process_message(self, message, data, exception):
            await self.post_process_event('message', message, data, exception)

        async def post_process_callback_query(self, message, data, exception):
            await self.post_process_event('callback_query', message, data, exception)

        async def post_process_my_chat_member(self, message, data, exception):
            await self.post_process_event('my_chat_member', message, data, exception)

        async def post_process_edited_message(self, message, data, exception):
            await self.post_process_event('edited_message', message, data, exception)

        async def post_process_channel_post(self, message, data, exception):
            await self.post_process_event('channel_post', message, data, exception)

        async def post_process_edited_channel_post(self, message, data, exception):
            await self.post_process_event('edited_channel_post', message, data, exception)

        async def post_process_business_connection(self, message, data, exception):
            await self.post_process_event('business_connection', message, data, exception)

        async def post_process_business_message(self, message, data, exception):
            await self.post_process_event('business_message', message, data, exception)

        async def post_process_edited_business_message(self, message, data, exception):
            await self.post_process_event('edited_business_message', message, data, exception)

        async def post_process_deleted_business_messages(self, message, data, exception):
            await self.post_process_event('deleted_business_messages', message, data, exception)

        async def post_process_message_reaction(self, message, data, exception):
            await self.post_process_event('message_reaction', message, data, exception)

        async def post_process_message_reaction_count(self, message, data, exception):
            await self.post_process_event('message_reaction_count', message, data, exception)

        async def post_process_inline_query(self, message, data, exception):
            await self.post_process_event('inline_query', message, data, exception)

        async def post_process_chosen_inline_result(self, message, data, exception):
            await self.post_process_event('chosen_inline_result', message, data, exception)

        async def post_process_shipping_query(self, message, data, exception):
            await self.post_process_event('shipping_query', message, data, exception)

        async def post_process_pre_checkout_query(self, message, data, exception):
            await self.post_process_event('pre_checkout_query', message, data, exception)

        async def post_process_purchased_paid_media(self, message, data, exception):
            await self.post_process_event('purchased_paid_media', message, data, exception)

        async def post_process_poll(self, message, data, exception):
            await self.post_process_event('poll', message, data, exception)

        async def post_process_poll_answer(self, message, data, exception):
            await self.post_process_event('poll_answer', message, data, exception)

        async def post_process_chat_member(self, message, data, exception):
            await self.post_process_event('chat_member', message, data, exception)

        async def post_process_chat_join_request(self, message, data, exception):
            await self.post_process_event('chat_join_request', message, data, exception)

        async def post_process_chat_boost(self, message, data, exception):
            await self.post_process_event('chat_boost', message, data, exception)

        async def post_process_removed_chat_boost(self, message, data, exception):
            await self.post_process_event('removed_chat_boost', message, data, exception)

        async def pre_process_message(self, message, data):
            pass

        async def pre_process_callback_query(self, message, data):
            pass

        async def pre_process_my_chat_member(self, message, data):
            pass

        async def pre_process_edited_message(self, message, data):
            pass

        async def pre_process_channel_post(self, message, data):
            pass

        async def pre_process_edited_channel_post(self, message, data):
            pass

        async def pre_process_business_connection(self, message, data):
            pass

        async def pre_process_business_message(self, message, data):
            pass

        async def pre_process_edited_business_message(self, message, data):
            pass

        async def pre_process_deleted_business_messages(self, message, data):
            pass

        async def pre_process_message_reaction(self, message, data):
            pass

        async def pre_process_message_reaction_count(self, message, data):
            pass

        async def pre_process_inline_query(self, message, data):
            pass

        async def pre_process_chosen_inline_result(self, message, data):
            pass

        async def pre_process_shipping_query(self, message, data):
            pass

        async def pre_process_pre_checkout_query(self, message, data):
            pass

        async def pre_process_purchased_paid_media(self, message, data):
            pass

        async def pre_process_poll(self, message, data):
            pass

        async def pre_process_poll_answer(self, message, data):
            pass

        async def pre_process_chat_member(self, message, data):
            pass

        async def pre_process_chat_join_request(self, message, data):
            pass

        async def pre_process_chat_boost(self, message, data):
            pass

        async def pre_process_removed_chat_boost(self, message, data):
            pass
except ImportError:
    telebot = False
    types = None
    TeleBot = None
    AsyncTeleBot = None


def object_to_dict(obj, handler_type: typing.Optional[HandlerType] = None) -> dict:
    if not telebot or not types:
        raise ImportError("pyTelegramBotAPI is not installed")

    handler_name = str(handler_type) if handler_type else None

    data = None

    update_id = -1
    if isinstance(obj, types.Update):
        update_id = obj.update_id
        for k, v in obj.__dict__.items():
            if k == "update_id":
                continue
            if v is not None and hasattr(v, "json"):
                handler_name = k
                data = v
                break
    else:
        data = obj

    if handler_name is None or data is None:
        raise TypeError("specify handler_type or pass instance of telebot.types.Update as an event")

    return {"update_id": update_id, handler_name: data.json}


def bind(sdk, bot):
    if not telebot:
        raise ImportError('pyTelegramBotAPI is not installed')
    
    if TeleBot is not None and isinstance(bot, TeleBot):
        bot.setup_middleware(TrackMiddleware(sdk))
    elif AsyncTeleBot is not None and isinstance(bot, AsyncTeleBot):
        bot.setup_middleware(AsyncTrackMiddleware(sdk))
