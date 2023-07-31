import pathlib


def get_project_folder():
    return pathlib.Path(__file__).resolve().parent.parent.parent


def get_data_folder():
    data_folder = get_project_folder() / 'data'
    data_folder.mkdir(exist_ok=True)
    return data_folder


def get_statements_folder(stock_id):
    data_folder = get_data_folder()
    statements_folder = data_folder / 'statements' / stock_id
    statements_folder.mkdir(parents=True, exist_ok=True)
    return statements_folder
