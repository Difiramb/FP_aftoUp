import asyncio
import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from funpaybotengine import Bot as FunPayBot
from vkbottle.bot import Bot as VKBot, Message

# ==========================================
# 1. НАСТРОЙКА И ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ==========================================
VK_TOKEN = os.environ.get("VK_TOKEN")
FUNPAY_GOLDEN_KEY = os.environ.get("FUNPAY_GOLDEN_KEY")

# ID вашего личного профиля ВК (чтобы бот слушался только вас).
# Обязательно добавьте переменную ADMIN_ID на Bothost!
ADMIN_ID = os.environ.get("ADMIN_ID") 

# Проверка, что все ключи на месте, чтобы бот не упал с непонятной ошибкой
if not VK_TOKEN:
    raise ValueError("❌ Ошибка: Не задана переменная окружения VK_TOKEN на Bothost!")
if not FUNPAY_GOLDEN_KEY:
    raise ValueError("❌ Ошибка: Не задана переменная окружения FUNPAY_GOLDEN_KEY на Bothost!")
if not ADMIN_ID:
    logging.warning("⚠️ ВНИМАНИЕ: Переменная ADMIN_ID не задана! Любой человек сможет управлять ботом.")

# Настройка логирования (чтобы вы видели, что происходит, в панели Bothost)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ КЛИЕНТОВ
# ==========================================
vk_bot = VKBot(token=VK_TOKEN)
funpay_bot = FunPayBot(golden_key=FUNPAY_GOLDEN_KEY)

# ==========================================
# 3. ФУНКЦИЯ ПОДНЯТИЯ ЛОТОВ
# ==========================================
async def raise_all_lots():
    """Асинхронная задача для поднятия всех лотов на FunPay."""
    logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск задачи по поднятию лотов...")
    try:
        # В библиотеке funpaybotengine метод может называться по-разному.
        # Если метод ниже выдаст ошибку AttributeError, проверьте документацию библиотеки.
        # Часто используется что-то вроде:
        # await funpay_bot.raise_all_lots() 
        
        # ЗАГЛУШКА (УДАЛИТЕ ЕЕ, КОГДА ПРОПИШЕТЕ ПРАВИЛЬНЫЙ МЕТОД):
        logger.info("✅ Все лоты успешно подняты (симуляция).")
        await asyncio.sleep(2) # Имитация задержки
        
    except Exception as e:
        logger.error(f"❌ Ошибка при поднятии лотов: {e}")

# ==========================================
# 4. ОБРАБОТЧИК КОМАНД В ВК
# ==========================================
@vk_bot.on.message(text=["поднять лоты", "raise", "Поднять лоты", "Поднять"])
async def manual_raise_handler(message: Message):
    """Обработчик ручной команды в VK."""
    
    # Проверка: если ADMIN_ID задан и сообщение пришло НЕ от вас — игнорируем
    if ADMIN_ID and str(message.from_id) != str(ADMIN_ID):
        await message.answer("⛔ У вас нет прав на управление этим ботом.")
        return

    await message.answer("🚀 Принято! Запускаю процесс поднятия лотов...")
    await raise_all_lots()
    await message.answer("✅ Процесс завершён. Бот продолжит работать в фоне.")

# ==========================================
# 5. ЗАПУСК БОТА И ПЛАНИРОВЩИКА
# ==========================================
async def main():
    # Настройка планировщика
    scheduler = AsyncIOScheduler()
    
    # Запуск каждые 2 часа. 
    # next_run_time=... означает, что первый раз бот поднимет лоты через 10 секунд после запуска.
    scheduler.add_job(
        raise_all_lots, 
        'interval', 
        hours=2, 
        next_run_time=datetime.now() + timedelta(seconds=10)
    )
    
    # Запускаем планировщик в фоне
    scheduler.start()
    logger.info("⏰ Планировщик запущен. Автоподнятие будет происходить каждые 2 часа.")

    # Запускаем VK-бота
    logger.info("🤖 Запуск VK-бота...")
    await vk_bot.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
