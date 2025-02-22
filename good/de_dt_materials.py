from db_utils import load_config, create_psycopg2_connection
import os


def de_dt_materials_main():
    
    config_path = 'config_to_connection.json'
    
    config = load_config(config_path)

    # Создаем подключение через psycopg2
    conn, cur = create_psycopg2_connection(config)

    try:
        # Запрос для получения данных из первой таблицы
        cur.execute("""
            SELECT "Material", "Temperature", "Orientation", "Time lapse", "Deformation", "Tension"
            FROM experiment_full_table
            ORDER BY "Material", "Time lapse";
        """)
        table1_data = cur.fetchall()

        # Запрос для получения данных из второй таблицы
        cur.execute("""
            SELECT "Material", "Beginning", "End"
            FROM lengths;
        """)
        table2_data = cur.fetchall()

        # Создаем словарь для хранения временных интервалов для каждого материала
        time_intervals = {row[0]: (row[1], row[2]) for row in table2_data}

        # Создаем словарь для хранения Tension для каждого материала
        tension_dict = {row[0]: row[5] for row in table1_data}

        # Создаем список для хранения результатов
        results = []

        # Обрабатываем данные для каждого материала
        for material, (beginning, end) in time_intervals.items():
            # Фильтруем данные по материалу и временному интервалу
            filtered_data = [
                row for row in table1_data
                if row[0] == material and beginning <= row[3] <= end
            ]

            if not filtered_data:
                continue  # Пропускаем, если нет данных в интервале

            # Находим начальную и конечную деформацию
            deformation_start = filtered_data[0][4]
            deformation_end = filtered_data[-1][4]

            # Вычисляем dE_dt
            time_interval = end - beginning
            dE_dt = (deformation_end - deformation_start) / time_interval if time_interval != 0 else 0.0

            # Добавляем результат
            results.append((
                material,
                filtered_data[0][1],  # Temperature
                filtered_data[0][2],  # Orientation
                dE_dt,
                tension_dict[material]  # Tension
            ))

        # Создаем новую таблицу в базе данных
        cur.execute("""
            CREATE TABLE IF NOT EXISTS de_dt_table (
                Material TEXT,
                Temperature FLOAT,
                Orientation TEXT,
                dE_dt FLOAT,
                Tension FLOAT
            );
        """)

        # Очищаем таблицу, если она уже существует
        cur.execute("TRUNCATE TABLE de_dt_table;")

        # Вставляем данные в новую таблицу
        insert_query = """
            INSERT INTO de_dt_table (Material, Temperature, Orientation, dE_dt, Tension)
            VALUES (%s, %s, %s, %s, %s);
        """
        cur.executemany(insert_query, results)

        # Фиксируем изменения
        conn.commit()
        print("Новая таблица успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка при выполнении операций с базой данных: {e}")
        conn.rollback()  # Откатываем изменения в случае ошибки
    finally:
        # Закрываем курсор и соединение
        cur.close()
        conn.close()
