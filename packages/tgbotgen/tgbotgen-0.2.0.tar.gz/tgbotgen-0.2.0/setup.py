from setuptools import setup, find_packages

setup(
    name="tgbotgen",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "tg-bot-init=tgbotgen.scaffold:run_scaffold",
        ],
    },
    install_requires=[
        "aiogram==3.3.0",
        "SQLAlchemy==2.0.40",
        "python-dotenv==0.9.0",
        "APScheduler==3.11.0",
        "aiosqlite==0.21.0",
        'gspread==6.2.1',
        'oauth2client==4.1.3',
        'google-api-python-client~=2.179.0'
    ],
    author="Александр Аваков",
    description="Генератор структуры проекта для Telegram-бота",
    python_requires=">=3.8",
)
