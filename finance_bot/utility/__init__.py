import pathlib


def get_project_folder():
    return pathlib.Path(__file__).resolve().parent.parent.parent


def get_data_folder():
    data_folder = get_project_folder() / 'data'
    data_folder.mkdir(exist_ok=True)
    return data_folder
