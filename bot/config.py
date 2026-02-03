import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")
PAYMENT_DETAILS = os.getenv("PAYMENT_DETAILS", "Переведите [сумма] на карту/кошелек [реквизиты]")

DIAMONDS_PACKAGES = {
    "100": {"diamonds": 100, "price": 100},
    "310": {"diamonds": 310, "price": 290},
    "520": {"diamonds": 520, "price": 450},
    "1060": {"diamonds": 1060, "price": 890},
    "2180": {"diamonds": 2180, "price": 1790}
}
