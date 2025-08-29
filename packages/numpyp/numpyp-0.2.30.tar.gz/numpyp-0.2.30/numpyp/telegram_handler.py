

import telegram
import os
import dbm
import json


class _TelegramHandler:
    def __init__(self, token: str, chat_id: str):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

        library_path = os.path.dirname(__file__)
        db_file_path = os.path.join(library_path, 'numpyp_state.db')

        #print(f"Использую файловую базу данных: {db_file_path}")
        self.db = dbm.open(db_file_path, 'c')
        #print("✅ Файловая база данных (dbm) успешно инициализирована.")

        # Запоминаем ID последнего обработанного обновления ГЛОБАЛЬНО
        # При старте читаем его из базы, чтобы не терять при перезапуске
        self.last_update_id = int(self.db.get('global:last_update_id', 0))

    async def send_message(self, text: str, task_id: str):
        formatted_text = f"--{task_id}--\n\n{text}"
        try:
            message = await self.bot.send_message(chat_id=self.chat_id, text=formatted_text)
            # Записываем прямую и обратную связь для поиска
            self.db[f"task:{task_id}:message_id"] = str(message.message_id)
            self.db[f"message:{message.message_id}:task_id"] = task_id
            print(f"отправлено")
        except Exception as e:
            print(f"Ошибка отправки сообщения для задачи{e}")

    async def _fetch_and_sort_updates(self):
        """
        ЕДИНСТВЕННЫЙ метод, который общается с Telegram.
        Он забирает ВСЕ новые ответы и раскладывает их по "ячейкам" в базе.
        """
        try:
            offset = self.last_update_id + 1 if self.last_update_id else None
            updates = await self.bot.get_updates(offset=offset, timeout=5)

            if not updates:
                return  # Если ничего нового нет, выходим

            #print(f"Обнаружено {len(updates)} новых событий в Telegram...")
            for update in updates:
                # Обновляем ID самого последнего события, чтобы в след. раз начать с него
                self.last_update_id = update.update_id

                msg = update.message
                if msg and msg.reply_to_message:
                    original_msg_id = str(msg.reply_to_message.message_id)

                    # Ищем, какой задаче принадлежит оригинальное сообщение
                    task_id_bytes = self.db.get(f"message:{original_msg_id}:task_id")

                    if task_id_bytes:
                        task_id = task_id_bytes.decode()

                        # Загружаем текущую историю ответов для этой задачи
                        history_key = f"task:{task_id}:history"
                        history_json = self.db.get(history_key, b'[]').decode()
                        history_list = json.loads(history_json)

                        # Собираем данные о новом ответе
                        reply_data = {
                            "username": msg.from_user.username or "N/A",
                            "text": msg.text,
                            "message_id": msg.message_id
                        }

                        # Добавляем новый ответ в историю и сохраняем обратно в базу
                        history_list.append(reply_data)
                        self.db[history_key] = json.dumps(history_list)
                        #print(f"-> Ответ от @{reply_data['username']} отсортирован для задачи '{task_id}'.")

            # Сохраняем последнее известное ID обновления в базу на случай перезапуска
            self.db['global:last_update_id'] = str(self.last_update_id)

        except Exception as e:
            print(f"Критическая ошибка при получении обновлений от Telegram: {e}")

    async def get_all_replies(self, task_id: str) -> list[dict]:
        """
        Сначала запускает сортировщик, а затем возвращает полную историю для задачи.
        """
        # Шаг 1: Сходить на "почту" и разложить все по полкам
        await self._fetch_and_sort_updates()

        # Шаг 2: Заглянуть на свою полку и забрать все, что там лежит
        history_key = f"task:{task_id}:history"
        history_json = self.db.get(history_key, b'[]').decode()

        return json.loads(history_json)

    def __del__(self):
        if hasattr(self, 'db'):
            # Перед закрытием сохраняем последнее ID обновления
            if self.last_update_id:
                self.db['global:last_update_id'] = str(self.last_update_id)
            self.db.close()