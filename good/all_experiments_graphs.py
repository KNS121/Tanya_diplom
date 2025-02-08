import matplotlib.pyplot as plt
from db_utils import load_config, create_psycopg2_connection
import os

def get_unique_material_orientation_pairs(config_path: str, table_name: str):
    config = load_config(config_path)
    unique_pairs = []
    conn, cur = None, None
    try:
        conn, cur = create_psycopg2_connection(config)
        cur.execute(f'SELECT DISTINCT "Material", "Orientation", "Temperature" FROM {table_name}')
        unique_pairs = cur.fetchall()
    except Exception as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return unique_pairs

def get_x_y_values(config_path: str, table_name: str, material: str, orientation: str, temperature: str):
    config = load_config(config_path)
    x_values, y_values = [], []
    conn, cur = None, None
    try:
        conn, cur = create_psycopg2_connection(config)
        cur.execute(
            f'SELECT "Time_lapse", "Deformation" FROM {table_name} WHERE "Material" = %s AND "Orientation" = %s AND "Temperature" = %s',
            (material, orientation, temperature)
        )
        rows = cur.fetchall()
        x_values = [row[0] for row in rows]
        y_values = [row[1] for row in rows]
    except Exception as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return x_values, y_values

def plot_x_y_values(x_values, y_values, material, orientation, temperature):
    
    plt.figure(figsize=(25, 20))
    plt.plot(x_values, y_values, label=f'{material}, {orientation}, {temperature}' , linewidth=2)
    plt.xlabel('Time_lapse, hour', fontsize=20)
    plt.ylabel('Deformation, %', fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.title(f'График для материала: {material}, Направление: {orientation}, Температура: {temperature}', fontsize=23)
    plt.grid(True)
    #plt.show()
    
    filename = os.path.join("graphs", f'{material}_orientation_{orientation}_temperature_{temperature}.png')
    plt.savefig(filename)
    plt.close()

def all_experiments_main():
    config_path = 'config_to_connection.json'
    table_name = 'experiment_full_table'

    unique_pairs = get_unique_material_orientation_pairs(config_path, table_name)
    #print("Уникальные пары (Material, Orientation):", unique_pairs)

    for material, orientation, temperature in unique_pairs:
        x_values, y_values = get_x_y_values(config_path, table_name, material, orientation, temperature)
        plot_x_y_values(x_values, y_values, material, orientation, temperature)