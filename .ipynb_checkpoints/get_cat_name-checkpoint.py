import os


def get_name_catalog(directory_path):

    items = os.listdir(directory_path)

    folders = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
    
    return folders