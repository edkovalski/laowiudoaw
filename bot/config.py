import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")
PAYMENT_DETAILS = f"""ПРАЙС-ЛИСТ

АЛМАЗЫ:
- 100+5 алмазов | 10.0 сомони
- 310+16 алмазов | 25.0 сомони  
- 520+26 алмазов | 48 сомони
- 1060+53 алмаза | 93 сомони
- 2180+109 алмазов | 185 сомони

ВАУЧЕРЫ:
- Ваучер на неделю (450) | 16.0 сомони
- Ваучер на месяц (2600) | 95.0 сомони

ПРОПУСКИ EVO:
- EVO пропуск 3 дня | 11 сомони
- EVO пропуск 7 дней | 14 сомони
- EVO пропуск 30 дней | 35 сомони

СПОСОБЫ ОПЛАТЫ:
Dushanbe City
Alif mobi 

АДМИНИСТРАТОР:
@legahome_001

Для оплаты переведите [сумма] сомони на указанные реквизиты"""

DIAMONDS_PACKAGES = {
    "100": {"diamonds": 105, "price": 10.0, "name": "100+5 алмазов"},
    "310": {"diamonds": 326, "price": 25.0, "name": "310+16 алмазов"},
    "520": {"diamonds": 546, "price": 48.0, "name": "520+26 алмазов"},
    "1060": {"diamonds": 1113, "price": 93.0, "name": "1060+53 алмаза"},
    "2180": {"diamonds": 2289, "price": 185.0, "name": "2180+109 алмазов"}
}

VOUCHER_PACKAGES = {
    "weekly": {"diamonds": 450, "price": 16.0, "name": "Ваучер на неделю (450)"},
    "monthly": {"diamonds": 2600, "price": 95.0, "name": "Ваучер на месяц (2600)"}
}

EVO_PACKAGES = {
    "3days": {"diamonds": 0, "price": 11.0, "name": "EVO пропуск 3 дня"},
    "7days": {"diamonds": 0, "price": 14.0, "name": "EVO пропуск 7 дней"},
    "30days": {"diamonds": 0, "price": 35.0, "name": "EVO пропуск 30 дней"}
}

PAYMENT_METHODS = "🏦 Dushanbe City\n💳 Alif mobi"
ADMIN_CONTACT = "@legahome_001"
