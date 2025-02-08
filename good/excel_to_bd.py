import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from db_utils import load_config, create_sqlalchemy_engine


class DatabaseManager:
    def __init__(self, config_path: str):
        """
        Инициализация менеджера базы данных.
        :param config_path: Путь к JSON-файлу с конфигурацией подключения.
        """
        self.config_path = config_path
        self.db_config = load_config(config_path)
        self.engine = create_sqlalchemy_engine(self.db_config)

    def test_connection(self):
        """
        Проверяет подключение к базе данных.
        """
        try:
            with self.engine.connect() as connection:
                print("Подключение к базе данных PostgreSQL прошло успешно!")
        except SQLAlchemyError as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def read_excel(self, excel_file_path: str) -> pd.DataFrame:
        """
        Читает данные из Excel-файла.
        :param excel_file_path: Путь к Excel-файлу.
        :return: DataFrame с данными.
        """
        try:
            df = pd.read_excel(excel_file_path)
            print("Данные из Excel успешно загружены:")
            print(df.head())
            return df
        except Exception as e:
            print(f"Ошибка при чтении Excel-файла: {e}")
            exit(1)

    def write_to_db(self, table_name: str, df: pd.DataFrame, if_exists: str = 'replace'):
        """
        Записывает данные из DataFrame в таблицу PostgreSQL.
        :param table_name: Имя таблицы в базе данных.
        :param df: DataFrame с данными.
        :param if_exists: Действие, если таблица уже существует ('replace', 'append', 'fail').
        """
        try:
            with self.engine.connect() as connection:
                df.to_sql(table_name, connection, if_exists=if_exists, index=False)
                print(f"Данные успешно перенесены в таблицу {table_name} базы данных {self.db_config['dbname']}!")
        except SQLAlchemyError as e:
            print(f"Ошибка при записи данных в базу данных: {e}")

    def close(self):
        """
        Закрывает подключение к базе данных.
        """
        self.engine.dispose()
        print("Подключение к базе данных закрыто.")


# Пример использования
def excel_to_bd_main():
    # Путь к конфигурационному файлу
    config_path = 'config_to_connection.json'

    # Создаем экземпляр менеджера базы данных
    db_manager = DatabaseManager(config_path)

    # Проверяем подключение к базе данных
    db_manager.test_connection()

    # Путь к Excel-файлу
    excel_file_path = 'FinalTableDatabase.xlsx'

    # Читаем данные из Excel
    df = db_manager.read_excel(excel_file_path)

    # Имя таблицы в PostgreSQL
    table_name = 'experiment_full_table'

    # Записываем данные в базу данных
    db_manager.write_to_db(table_name, df, if_exists='replace')

    # Закрываем подключение к базе данных
    db_manager.close()