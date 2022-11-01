from dotenv import load_dotenv
import os
from lib import Core

load_dotenv()


cogs = [
    "tts.voice",
    "cogs.admin",
]


if __name__ == "__main__":
    TOKEN = os.environ.get("VOICE")
    bot = Core(
        "sentry_url",
        cogs,
    )
    
    bot.run(TOKEN)
