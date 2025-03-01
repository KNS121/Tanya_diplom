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

        # Создаем словарь для группировки данных по Temperature и Orientation
        grouped_data = {}

        # Обрабатываем данные для каждого материала
        for row in table1_data:
            material, temperature, orientation, time_lapse, deformation, tension = row

            # Фильтруем данные по строгому временному интервалу
            if material in time_intervals:
                beginning, end = time_intervals[material]
                if beginning < time_lapse < end:  # Строгое условие
                    key = (temperature, orientation)

                    if key not in grouped_data:
                        grouped_data[key] = []

                    # Добавляем данные, если материал еще не был добавлен
                    if not any(item[0] == material for item in grouped_data[key]):
                        # Находим все данные для материала в заданном интервале
                        filtered_data = [
                            r for r in table1_data
                            if r[0] == material and beginning < r[3] < end  # Строгое условие
                        ]
                        if filtered_data:
                            # Находим минимальное и максимальное время в интервале
                            time_lapses = [r[3] for r in filtered_data]
                            time_start = min(time_lapses)
                            time_end = max(time_lapses)
                            time_interval = time_end - time_start  # Точный интервал

                            # Находим начальную и конечную деформацию
                            deformation_start = filtered_data[0][4]
                            deformation_end = filtered_data[-1][4]
                            dE_dt = (deformation_end - deformation_start) / time_interval if time_interval != 0 else 0.0

                            # Добавляем данные с расчетом dE_dt
                            grouped_data[key].append((
                                material,
                                temperature,
                                orientation,
                                time_interval,
                                deformation,
                                tension,
                                dE_dt
                            ))

        # Создаем таблицы для каждой группы
        for (temperature, orientation), rows in grouped_data.items():
            # Название таблицы формируем на основе Temperature и Orientation
            table_name = f"temp_{temperature}_orient_{orientation}"

            # Удаляем таблицу, если она уже существует
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")

            # Создаем новую таблицу с добавлением столбца dE_dt
            cur.execute(f"""
                CREATE TABLE {table_name} (
                    "Material" TEXT,
                    "Temperature" FLOAT,
                    "Orientation" TEXT,
                    "Time lapse" FLOAT,
                    "Deformation" FLOAT,
                    "Tension" FLOAT,
                    "dE_dt" FLOAT
                );
            """)

            # Вставляем данные в таблицу
            insert_query = f"""
                INSERT INTO {table_name} ("Material", "Temperature", "Orientation", "Time lapse", "Deformation", "Tension", "dE_dt")
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cur.executemany(insert_query, rows)

            print(f"Таблица {table_name} успешно создана и заполнена!")

        # Фиксируем изменения
        conn.commit()

    except Exception as e:
        print(f"Ошибка при выполнении операций с базой данных: {e}")
        conn.rollback()  # Откатываем изменения в случае ошибки
    finally:
        # Закрываем курсор и соединение
        cur.close()
        conn.close()