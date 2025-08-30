# Dashgram SDK

A Python SDK for Dashgram - Analytics and tracking for Telegram bots with seamless integration for popular Python Telegram bot frameworks.

[![PyPI version](https://badge.fury.io/py/dashgram.svg)](https://badge.fury.io/py/dashgram)
[![Python versions](https://img.shields.io/pypi/pyversions/dashgram.svg)](https://pypi.org/project/dashgram/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🚀 **Easy Integration** - Works with aiogram, python-telegram-bot, and pyTelegramBotAPI
- 📊 **Event Tracking** - Track messages, callback queries, and all Telegram update types
- 🔄 **Framework Agnostic** - Automatically detects your bot framework
- ⚡ **Async Support** - Full async/await support with automatic sync wrapper
- 🛡️ **Error Handling** - Robust error handling with configurable exception suppression
- 🎯 **Invitation Tracking** - Track user invitations and referrals

## Supported Frameworks

- [aiogram](https://github.com/aiogram/aiogram) (v3.x)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) (v21.x)
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (v4.x)

## Installation

```bash
pip install dashgram
```

## Quick Start

### Basic Usage

```python
from dashgram import Dashgram, HandlerType

# Initialize the SDK with your project credentials
sdk = Dashgram(
    project_id="your_project_id",
    access_key="your_access_key"
)

# Track any Telegram update
sdk.track_event(update)

# Track a specific event type
sdk.track_event(event_data, HandlerType.MESSAGE)

# Mark user as invited by another user (for referral analytics)
sdk.invited_by(user_id, inviter_user_id)
```

The `event_data` parameter should contain the update data in raw Telegram API format, or the corresponding update/message object from your framework (aiogram, python-telegram-bot, or pyTelegramBotAPI).

### Framework Integration

#### aiogram

Choose the integration method that best fits your needs:

```python
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update
from dashgram import Dashgram, HandlerType

# Initialize SDK with your credentials
sdk = Dashgram(
    project_id="your_project_id", 
    access_key="your_access_key"
)

dp = Dispatcher()

# Option 1: Automatic tracking (recommended for most use cases)
sdk.bind_aiogram(dp)

@dp.message()
async def handle_message(message: Message, event_update: Update):
    # Option 2: Manual tracking with full update data
    await sdk.track_event(event_update)
    ...

@dp.edited_message()
async def handle_edited_message(edited_message: Message):
    # Option 3: Manual tracking with specific handler type
    await sdk.track_event(edited_message, HandlerType.EDITED_MESSAGE)
    ...
```

#### python-telegram-bot (v21.x)

```python
from telegram.ext import Application, MessageHandler, filters
from dashgram import Dashgram

# Initialize SDK with your credentials
sdk = Dashgram(
    project_id="your_project_id", 
    access_key="your_access_key"
)

async def handle_message(update, context):
    # Manual tracking for specific events
    await sdk.track_event(update)
    ...

application = Application.builder().token("YOUR_BOT_TOKEN").build()
application.add_handler(MessageHandler(filters.TEXT, handle_message))

# Automatic tracking for all events
sdk.bind_telegram(application)

application.run_polling()
```

#### pyTelegramBotAPI

```python
import telebot
from dashgram import Dashgram, HandlerType

# Initialize SDK with your credentials
sdk = Dashgram(
    project_id="your_project_id", 
    access_key="your_access_key"
)

bot = telebot.TeleBot("YOUR_BOT_TOKEN", use_class_middlewares=True)

# Automatic tracking for all events
sdk.bind_telebot(bot)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Manual tracking for specific events
    sdk.track_event(message, HandlerType.MESSAGE)
    ...

bot.polling()
```

## API Reference

### Dashgram Class

#### Constructor

```python
Dashgram(
    project_id: Union[int, str],
    access_key: str,
    *,
    api_url: Optional[str] = None,
    origin: Optional[str] = None
)
```

**Parameters:**
- `project_id` - Your Dashgram project ID (found in your project settings)
- `access_key` - Your Dashgram access key (found in your project settings)
- `api_url` - Custom API URL (defaults to `https://api.dashgram.io/v1`)
- `origin` - Custom origin string for SDK usage analytics (optional)

#### Methods

##### track_event()

```python
async def track_event(
    event,
    handler_type: Optional[HandlerType] = None,
    suppress_exceptions: bool = True
) -> bool
```

Track a Telegram event or update. This method automatically detects the framework and extracts relevant data.

**Parameters:**
- `event` - Telegram event object or dictionary (from any supported framework)
- `handler_type` - Type of handler (optional if event is a framework object)
- `suppress_exceptions` - Whether to suppress exceptions (default: True)

**Returns:** `bool` - True if successful, False otherwise

##### invited_by()

```python
async def invited_by(
    user_id: int,
    invited_by: int,
    suppress_exceptions: bool = True
) -> bool
```

Track user invitation/referral for analytics purposes.

**Parameters:**
- `user_id` - ID of the invited user
- `invited_by` - ID of the user who sent the invitation
- `suppress_exceptions` - Whether to suppress exceptions (default: True)

**Returns:** `bool` - True if successful, False otherwise

##### Framework Binding Methods

```python
def bind_aiogram(dp) -> None
def bind_telegram(app, group: int = -1, block: bool = False) -> None
def bind_telebot(bot) -> None
```

Automatically track all events for the respective framework. These methods integrate middleware or handlers to capture all bot interactions.

## Examples

### Complete aiogram Example

```python
import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dashgram import Dashgram, HandlerType

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize SDK with environment variables
sdk = Dashgram(
    project_id=getenv("PROJECT_ID"),
    access_key=getenv("ACCESS_KEY")
)

dp = Dispatcher()

# Manual tracking example
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

# Automatic tracking for all events
sdk.bind_aiogram(dp)

async def main():
    bot = Bot(token=getenv("BOT_TOKEN"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

### Complete python-telegram-bot Example

```python
import logging
from os import getenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from dashgram import Dashgram

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize SDK with environment variables
sdk = Dashgram(
    project_id=getenv("PROJECT_ID"),
    access_key=getenv("ACCESS_KEY")
)

async def start(update: Update, context):
    await update.message.reply_text("Hello!")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

def main():
    application = Application.builder().token(getenv("BOT_TOKEN")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Automatic tracking for all events
    sdk.bind_telegram(application)
    
    application.run_polling()

if __name__ == "__main__":
    main()
```

### Complete pyTelegramBotAPI Example

```python
import logging
from os import getenv

import telebot
from dashgram import Dashgram

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize SDK with environment variables
sdk = Dashgram(
    project_id=getenv("PROJECT_ID"),
    access_key=getenv("ACCESS_KEY")
)

bot = telebot.TeleBot(getenv("BOT_TOKEN"), use_class_middlewares=True)

# Automatic tracking for all events
sdk.bind_telebot(bot)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello!")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, message.text)

if __name__ == "__main__":
    bot.polling()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: team@dashgram.io
- 📖 Documentation: [docs.dashgram.io](https://docs.dashgram.io)
- 🐛 Issues: [GitHub Issues](https://github.com/Dashgram/sdk-python/issues)
- 💬 Community: [Telegram Channel](https://t.me/dashgram_live)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
