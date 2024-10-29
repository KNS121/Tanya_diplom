import pandas as pd

def try_to_read_csv(path, *encodings):
    
    for enc in encodings:
    
        try:
            df = pd.read_csv(path, encoding = enc)
            return df
    
        except UnicodeDecodeError:
            continue

        except:
            print(f"Ошибка при чтении файла с кодировкой {encoding}: {e}")
            continue
    raise ValueError("Не удалось прочитать файл с использованием предоставленных кодировок")