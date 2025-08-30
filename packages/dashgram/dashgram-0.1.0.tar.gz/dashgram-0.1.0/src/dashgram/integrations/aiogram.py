# aiogram integration
import typing

from dashgram.enums import HandlerType

try:
    from aiogram.utils.serialization import deserialize_telegram_object_to_python
    from aiogram import types, Dispatcher
    aiogram = True
except ImportError as e:
    aiogram = False
    types = None
    Dispatcher = typing.Any
    deserialize_telegram_object_to_python = None


def object_to_dict(obj, handler_type: typing.Optional[HandlerType] = None) -> dict:
    if not aiogram or not deserialize_telegram_object_to_python or not types:
        raise ImportError("aiogram is not installed")

    if not isinstance(obj, types.Update):
        if handler_type is None:
            raise TypeError("specify handler_type or pass instance of aiogram.types.Update as an event")

        obj = types.Update(update_id=-1, **{str(handler_type): obj})

    raw_data = deserialize_telegram_object_to_python(obj)
    data = rename_key(raw_data, "from_user", "from")

    return data


def rename_key(d, old_key, new_key):
    nd = {}

    for key, value in d.items():
        if key == old_key:
            nd[new_key] = d[old_key]
        else:
            nd[key] = value

    for key, value in nd.items():
        if isinstance(value, dict):
            nd[key] = rename_key(value, old_key, new_key)

    return nd


def bind(sdk, dp):
    if not aiogram:
        raise ImportError("aiogram is not installed")

    @dp.update.outer_middleware()
    async def track_event_middleware(
            handler,
            event,
            data
    ):
        await sdk.track_event(event)
        return await handler(event, data)
