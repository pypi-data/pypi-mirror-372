from .code import *
from .code_t import *
from .see import *

import pyperclip
import os
from dotenv import load_dotenv
from .telegram_handler import _TelegramHandler

_telegram_instance: _TelegramHandler | None = None


def _auto_initialize_if_needed():
    """Автоматически настраивает модуль, используя redislite."""
    global _telegram_instance
    if _telegram_instance:
        return

    #print("🔧 Первая попытка вызова. Автоматическая настройка...")

    library_path = os.path.dirname(__file__)
    dotenv_path = os.path.join(library_path, '.env')

    if not os.path.exists(dotenv_path):
        raise FileNotFoundError(f"Не найден .env файл внутри библиотеки! Поместите .env по этому пути: {library_path}")

    load_dotenv(dotenv_path=dotenv_path)

    # --- УПРОЩЕННАЯ ЛОГИКА ---
    # Загружаем только то, что нужно
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not all([token, chat_id]):
        raise ValueError("Настройки TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не найдены или пусты в .env файле.")

    # Создаем экземпляр обработчика. Он сам разберется с Redis.
    _telegram_instance = _TelegramHandler(token=token, chat_id=chat_id)
    #print("Модуль успешно авто-инициализирован.")


async def call(text: str, task_id: str):
    """
    Асинхронно отправляет сообщение и регистрирует задачу с уникальным ID.
    :param text: Текст сообщения.
    :param task_id: Уникальный строковый идентификатор этой задачи.
    """
    _auto_initialize_if_needed()
    await _telegram_instance.send_message(text, task_id)

async def ans(task_id: str) :
    """
    Асинхронно проверяет и возвращает ПОЛНУЮ историю ответов для задачи.
    """
    _auto_initialize_if_needed()

    replies_list = await _telegram_instance.get_all_replies(task_id)

    if replies_list:
        # print(f"--- История ответов для задачи '{task_id}' (всего: {len(replies_list)}) ---")
        last_text = ""
        for reply in replies_list:
            username = reply.get('username', 'N/A')
            last_text = reply.get('text', '')


            pyperclip.copy(last_text)
            pyperclip.paste()

    else:
        print(f"нет")

    #return replies_list