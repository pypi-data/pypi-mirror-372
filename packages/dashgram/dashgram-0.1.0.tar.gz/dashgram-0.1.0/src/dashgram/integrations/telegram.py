# python-telegram-bot integration
try:
    from telegram.ext import BaseHandler
    telegram = True
except ImportError:
    telegram = False
    BaseHandler = None


def object_to_dict(obj, *args, **kwargs) -> dict:
    if not telegram:
        raise ImportError("python-telegram-bot is not installed")
    return obj.to_dict()


def bind(sdk, app, group: int = -1, block: bool = False):
    if not telegram or not BaseHandler:
        raise ImportError("python-telegram-bot is not installed")

    class UpdateHandler(BaseHandler):
        def check_update(self, update):
            return True

    async def track_update(update, context) -> None:
        await sdk.track_event(update)

    app.add_handler(UpdateHandler(track_update, block=block), group=group)