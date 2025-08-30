import os
from pathlib import Path


def create_file(path: Path, content: str = ''):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding='utf-8')


def run_scaffold():
    base = Path.cwd()

    files = {
        "bot/handler.py": '''import asyncio
import os.path
import re
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger        # Триггеры для функций
from apscheduler.triggers.date import DateTrigger


import config
from config import Config
from bot import keyboards as kb
from utils import msg_ids, logger, auto_state_clear
import db
import services as bridge

dp = Dispatcher()
bot = Bot(token=Config.BOT_TOKEN)
user_data = {}
scheduler = AsyncIOScheduler()


class Reg(StatesGroup):
    """Класс для FSM-состояний. Можно добавить несколько разных состояний,
    чтобы проводить процессы сбора данных с пользователя"""
    # state = State() - Пример состояния
    pass


@dp.message(CommandStart())
@auto_state_clear()
async def start(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    msg = await message.answer('Приветственное сообщение')
    msg_ids[uid].add(msg.message_id)


@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    uid = callback.from_user.id
    message = callback.message
    data = callback.data
    if data == 'main_menu':
        try:
            await bot.delete_messages(uid, list(msg_ids[uid]))
        except TelegramBadRequest:
            logger.error(f"Ошибка при удалении сообщений для пользователя {uid}")
        try:
            await message.edit_text('Главное меню:',
                                    reply_markup=kb.start_keyboard)
        except TelegramBadRequest:
            try:
                await message.delete()
            except Exception as e:
                logger.error(f'Ошибка: {e}')
            await message.answer('Главное меню:',
                                 reply_markup=kb.start_keyboard)
    elif data == 'about':
        await message.answer(
            'Текст обо мне:\\n'
            'Я - шаблон для бота. Можешь изменить и сделать меня таким, как тебе захочется',
            reply_markup=kb.back
        )
    elif data == 'clear':
        await message.delete()
    await callback.answer()


@dp.message()
async def message_handler(message: Message):
    """Обработчик сообщений от пользователя, которых бот не ожидает увидеть. Просто удаляет их"""
    await message.delete()


async def delete_message_after(message: Message, timeout: int = 86400):
    """Удаление сообщения после промежутка времени

    :param message: Объект сообщения, которое надо удалить.
    :param timeout: Время, после которого сообщение должно быть удалено.
    """
    await asyncio.sleep(timeout)
    try:
        await message.delete()
    except TelegramBadRequest as e:
        logger.error(f'Ошибка при удалении сообщений: {e}')


def setup_scheduler(scheduler_: AsyncIOScheduler):
    """Функция для установки задач для планировщика"""
    scheduler_.remove_all_jobs()  # сначала очищаем (если нужно)
    # scheduler.add_job(
    #     func,
    #     trigger=Trigger(minutes=10)
    # ) - поменять func на название нужной функции, и поставить триггер
    scheduler_.start()  # затем запускаем планировщик


async def main():
    await db.init_db()
    setup_scheduler(scheduler_=scheduler)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # только в конце запускаем бота
''',
        "bot/keyboards.py": '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Обо мне', callback_data='about')],
])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Назад', callback_data='main_menu')]
])

clear = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Назад', callback_data='clear')]
])''',

        "db/requests.py": '''import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from db.models import async_session, User


async def create_user(
        uid: int
) -> Optional[dict]:
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.uid == uid))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            return existing_user.as_dict()
        new_user = User(
            uid=uid,
        )
        session.add(new_user)
        await session.commit()
        return new_user.as_dict()


async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [user.as_dict() for user in users]


async def get_user_by_uid(uid: int):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.uid == uid))
        user = result.scalar_one_or_none()
        if user:
            return user.as_dict()
        return None''',
        "db/models.py": '''from typing import cast

from sqlalchemy import String, Float, ForeignKey, Integer, func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Mapper
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

engine = create_async_engine(url='sqlite+aiosqlite:///db/database/users.sqlite3')
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для создания моделей в БД"""

    def as_dict(self) -> dict:
        """Функция для представления записи в БД в виде словаря в формате
        {'названия поля в БД': 'Значение поля в БД'}

        :returns dict:
        """
        mapper: Mapper = cast(Mapper, inspect(self).mapper)
        return {
            column.key: getattr(self, column.key)
            for column in mapper.column_attrs
        }


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
''',
        "db/__init__.py": '''from db.requests import *
from db.models import *''',
        "db/database/.gitignore": "*.sqlite3",

        "keys/.gitignore": "*.*",

        "logger/logs/.gitignore": '''*.log''',
        "logger/file_logger.py": '''import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from config import Config

# Настройка директории для логов
# logs_directory = "./logger"
# if not os.path.exists(logs_directory):
#     os.makedirs(logs_directory)

# Формат логов
# log_format = "[%(asctime)s] %(levelname)s %(source)s: %(message)s"
log_format = "[%(asctime)s] %(levelname)s %(source)s %(funcName)s:%(lineno)d - %(message)s"


class CustomLogger:
    """
    Класс для создания кастомного логгера с поддержкой вывода в файл, консоль или оба варианта.
    """

    def __init__(self, source: str,
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 base_dir: str = "./log",
                 log_rotate_days: int = Config.LOG_ROTATE_DAYS):
        """
        Инициализация логгера.

        :param source: Источник логов (например, "System" или "user_123").
        :param log_to_file: Включить запись логов в файл (по умолчанию True).
        :param log_to_console: Включить вывод логов в консоль (по умолчанию True).
        :param base_dir: Директория для хранения логов (по умолчанию "./log").
        :param log_rotate_days: Период ротации логов в днях (по умолчанию 1 день).
        """
        self.source = source
        self.logger = logging.getLogger(f"custom_logger_{source}")
        self.logger.setLevel(logging.INFO)  # Устанавливаем минимальный уровень логирования

        # Очистка старых обработчиков
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Создаем директорию для логов, если она не существует
        self.log_directory = base_dir
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # Формат логов
        self.formatter = logging.Formatter(log_format)

        # Настройка обработчиков
        if log_to_file:
            self._setup_file_handler(log_rotate_days)
        self._setup_console_handlers(log_to_console)

    def destroy(self):
        """
        Закрытие всех обработчиков логгера.
        """
        for handler in self.logger.handlers[:]:
            try:
                handler.close()
                self.logger.removeHandler(handler)
            except Exception as e:
                print(f"Ошибка при закрытии обработчика: {e}")

    def _setup_file_handler(self, log_rotate_days: int):
        """
        Настройка обработчика для записи логов в файл.

        :param log_rotate_days: Период ротации логов в днях.
        """
        log_file_path = os.path.join(self.log_directory, f"{self.source}_{datetime.now().strftime('%Y_%m_%d')}.log")
        file_handler = TimedRotatingFileHandler(
            log_file_path,
            when="midnight",
            interval=log_rotate_days,
            backupCount=5,
            encoding='utf-8',
            delay=True  # Отложить открытие файла до первой записи
        )
        file_handler.setLevel(logging.DEBUG)  # Записываем все уровни логов в файл
        file_handler.setFormatter(self.formatter)

        # Переопределение имени файла при ротации
        def rename_rotated_logs(prefix):
            def namer(default_name):
                base_filename, ext = os.path.splitext(os.path.basename(default_name))
                rotated_time = base_filename.split(".")[1]
                new_filename = f"{prefix}_{rotated_time}{ext}"
                return os.path.join(self.log_directory, new_filename)
            return namer

        file_handler.namer = rename_rotated_logs(self.source)

        # Переопределение метода doRollover для закрытия файлов
        original_do_rollover = file_handler.doRollover

        def custom_do_rollover():
            original_do_rollover()  # Вызов оригинального метода
            for handler in self.logger.handlers[:]:
                if isinstance(handler, TimedRotatingFileHandler):
                    try:
                        handler.stream.close()  # Явно закрыть файл
                    except Exception as e:
                        c = 1
                        # logger.error(f"Ошибка при закрытии файла: {e}")

        file_handler.doRollover = custom_do_rollover

        self.logger.addHandler(file_handler)

    def _setup_console_handlers(self, log_to_console: bool):
        """
        Настройка обработчиков для вывода логов в консоль.

        :param log_to_console: Включить вывод логов в консоль.
        """
        # Обработчик для вывода ERROR и CRITICAL всегда
        error_console_handler = logging.StreamHandler()
        error_console_handler.setLevel(logging.ERROR)  # Только ERROR и выше
        error_console_handler.setFormatter(self.formatter)
        self.logger.addHandler(error_console_handler)

        # Обработчик для вывода остальных уровней только при log_to_console=True
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)  # Все уровни логов
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)

    def _log(self, level: int, message: str):
        """
        Внутренний метод для логирования сообщений.

        :param level: Уровень логирования (например, logging.INFO).
        :param message: Сообщение для логирования.
        """
        self.logger.log(level, message, extra={"source": self.source})

    def info(self, message: str):
        """Логирование информационных сообщений."""
        self._log(logging.INFO, message)

    def error(self, message: str):
        """Логирование сообщений об ошибках."""
        self._log(logging.ERROR, message)

    def warning(self, message: str):
        """Логирование предупреждений."""
        self._log(logging.WARNING, message)

    def debug(self, message: str):
        """Логирование отладочных сообщений."""
        self._log(logging.DEBUG, message)

    def critical(self, message: str):
        """Логирование критических ошибок."""
        self._log(logging.CRITICAL, message)''',

        "services/__init__.py": '''from services import google_api as ggl''',
        "services/google_api.py": '''import io
import os
import re

import gspread
from gspread import SpreadsheetNotFound
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from utils import logger
from config import Config

SHEET_ID = Config.SHEET_ID
FOLDER_ID = Config.FOLDER_ID
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_CREDENTIALS_JSON, SCOPES)
client = gspread.authorize(creds)


drive_service = build('drive', 'v3', credentials=creds)


async def send_info(info: list):
    logger.info('Called send_info')
    sheet = client.open_by_key(SHEET_ID).sheet1
    result = sheet.append_row(info)
    logger.info(f'Результат отправки данных в таблицу: {result}')
    return result


async def get_info():
    logger.info('fetching info from google sheet')
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet("акции")
        data = sheet.get_all_values()
        rows = data[1:]  # Skip the header row
        logger.info('Data read successfully')
    except SpreadsheetNotFound:
        logger.error('Таблица не найдена. Проверьте корректность ID таблицы')
        return None
    return rows


def download_file_from_drive(file_id: str, filename: str, dest_folder: str = "vpn_configs") -> str:
    os.makedirs(dest_folder, exist_ok=True)
    request = drive_service.files().get_media(fileId=file_id)

    file_path = os.path.join(dest_folder, filename)
    with io.FileIO(file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    return file_path


def transform_google_drive_link(link: str) -> str:
    """Преобразует обычную ссылку Google Диска в прямую ссылку для скачивания."""
    match = re.search(r"https://drive\.google\.com/file/d/([^/]+)/view", link)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return link''',

        "static/.gitignore": '*.*',

        "utils/__init__.py": "from utils.utils import *",
        "utils/utils.py": '''import asyncio
import os
from collections import defaultdict
from functools import wraps

from aiogram.fsm.context import FSMContext

from logger.file_logger import CustomLogger
from config import BASE_DIR


user_country = {}
msg_ids: dict[int, set] = defaultdict(set)
base_dir = os.path.join(BASE_DIR, 'logger', 'logs')
logger = CustomLogger('bot_log', base_dir=base_dir)
logger.info('logger initialized')

user_timers = {}
users = {}


def auto_state_clear(timeout: int = 900):
    def decorator(func):
        @wraps(func)
        async def wrapper(message, state: FSMContext, *args, **kwargs):
            user_id = message.from_user.id

            if user_id in user_timers:
                task = user_timers[user_id]
                if not task.done():
                    task.cancel()

            async def timer():
                try:
                    await asyncio.sleep(timeout)
                    await state.clear()
                    users.pop(user_id, None)
                    user_timers.pop(user_id, None)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Ошибка в таймере для {user_id}: {e}")

            user_timers[user_id] = asyncio.create_task(timer())

            return await func(message, state, *args, **kwargs)

        return wrapper
    return decorator''',

        ".env.example": '''BOT_TOKEN=
    GOOGLE_CREDENTIALS_JSON=keys/google_service_key.json
    SHEET_ID=
    FOLDER_ID=
    MANAGER_ID=
    CHANNEL_ID=''',
        ".env.local": "",
        ".gitignore": """.idea/
    __pycache__/
    .venv/
    .qodo/
    *.sqlite3
    .env.local
    """,
        "README.md": "",
        "config.py": '''import os

    from dotenv import load_dotenv

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Загрузка переменных окружения
    if os.path.exists(os.path.join(BASE_DIR, '.env.local')):
        load_dotenv(os.path.join(BASE_DIR, '.env.local'))
    else:
        load_dotenv(os.path.join(BASE_DIR, '.env'))


    class Config:
        BOT_TOKEN = os.getenv('BOT_TOKEN')
        DB_URL = f'sqlite+aiosqlite:///{BASE_DIR}/db/database/db.sqlite3'

        FOLDER_ID = os.getenv('FOLDER_ID')
        SHEET_ID = os.getenv('SHEET_ID')
        GOOGLE_CREDENTIALS_JSON = os.path.join(BASE_DIR, os.getenv('GOOGLE_CREDENTIALS_JSON'))
        MANAGER_ID = os.getenv('MANAGER_ID')
        CHANNEL_ID = os.getenv('CHANNEL_ID')
        LOG_ROTATE_DAYS = 1''',
        "main.py": '''import asyncio
import logging

from bot.handler import main


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')''',
        "requirements.txt": '''SQLAlchemy~=2.0.40
APScheduler~=3.11.0
aiogram~=3.3.0
gspread~=6.2.1
oauth2client~=4.1.3
google-api-python-client~=2.179.0
python-dotenv~=0.9.0'''
    }

    dirs = ["static/"]

    for path_str, content in files.items():
        create_file(base / path_str, content)

    for dir_str in dirs:
        (base / dir_str).mkdir(parents=True, exist_ok=True)

    print("✅ Структура проекта успешно создана.")
