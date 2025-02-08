import json
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from psycopg2 import OperationalError


def load_config(config_path: str) -> dict:
    """
    Загружает конфигурацию подключения из JSON-файла.
    :param config_path: Путь к JSON-файлу.
    :return: Словарь с конфигурацией.
    """
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл конфигурации {config_path} не найден!")
        exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка в формате JSON в файле {config_path}!")
        exit(1)


def create_psycopg2_connection(config: dict):
    """
    Создает подключение к базе данных через psycopg2.
    :param config: Словарь с конфигурацией подключения.
    :return: Объект подключения и курсор.
    """
    try:
        conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        cur = conn.cursor()
        return conn, cur
    except OperationalError as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        exit(1)


def create_sqlalchemy_engine(config: dict):
    """
    Создает подключение к базе данных через SQLAlchemy.
    :param config: Словарь с конфигурацией подключения.
    :return: Объект подключения SQLAlchemy.
    """
    connection_string = (
        f"postgresql+psycopg2://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['dbname']}"
    )
    return create_engine(connection_string)