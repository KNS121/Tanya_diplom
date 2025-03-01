import numpy as np
from db_utils import load_config, create_psycopg2_connection
from sklearn.linear_model import LinearRegression


def find_constants():
    config_path = 'config_to_connection.json'
    config = load_config(config_path)

    """
    Находит константы A и n для уравнения de_dt = A * Tension^n
    для каждого сочетания температуры и ориентации, используя метод наименьших квадратов.
    """
    conn, cur = create_psycopg2_connection(config)

    try:
        # Получаем список таблиц с данными
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'temp_%_orient_%';
        """)
        tables = cur.fetchall()

        # Создаем таблицу для хранения результатов, если она еще не существует
        cur.execute("""
            CREATE TABLE IF NOT EXISTS constants_table (
                "Orient" TEXT,
                "Temp" FLOAT,
                "A" FLOAT,
                "n" FLOAT
            );
        """)

        # Очищаем таблицу, если она уже существует
        cur.execute("TRUNCATE TABLE constants_table;")

        # Создаем список для хранения результатов
        results = []

        # Обрабатываем каждую таблицу
        for table in tables:
            table_name = table[0]

            # Получаем данные из таблицы
            cur.execute(f"""
                SELECT "Tension", "dE_dt"
                FROM {table_name};
            """)
            data = cur.fetchall()

            if not data:
                continue  # Пропускаем пустые таблицы

            # Фильтруем данные: удаляем строки, где Tension или dE_dt <= 0
            filtered_data = [
                row for row in data
                if row[0] > 0 and row[1] > 0
            ]

            if not filtered_data:
                print(f"В таблице {table_name} нет подходящих данных (Tension и dE_dt должны быть > 0).")
                continue

            # Подготовка данных для регрессии
            tensions = np.array([row[0] for row in filtered_data])
            de_dt = np.array([row[1] for row in filtered_data])

            # Логарифмируем данные
            log_tensions = np.log(tensions)
            log_de_dt = np.log(de_dt/(3600*100))

            # Создаем матрицу X и вектор y
            X = np.vstack([np.ones_like(log_tensions), log_tensions]).T
            y = log_de_dt

            # Решаем методом наименьших квадратов: beta = (X^T X)^-1 X^T y
            beta = np.linalg.inv(X.T @ X) @ X.T @ y

            # Получаем коэффициенты
            log_A = beta[0]
            n = beta[1]
            A = np.exp(log_A)

            # Извлекаем температуру и ориентацию из имени таблицы
            parts = table_name.split('_')
            temp = float(parts[1])  # Температура
            orient = parts[3]       # Ориентация

            # Сохраняем результаты
            results.append((orient, temp, A, n))

        # Вставляем данные в таблицу constants_table
        insert_query = """
            INSERT INTO constants_table ("Orient", "Temp", "A", "n")
            VALUES (%s, %s, %s, %s);
        """
        cur.executemany(insert_query, results)

        # Фиксируем изменения
        conn.commit()
        print("Результаты успешно записаны в таблицу constants_table!")

    except Exception as e:
        print(f"Ошибка при выполнении операций с базой данных: {e}")
        conn.rollback()  # Откатываем изменения в случае ошибки
    finally:
        # Закрываем курсор и соединение
        cur.close()
        conn.close()
