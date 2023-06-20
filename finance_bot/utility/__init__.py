import pathlib


def get_project_folder():
    return pathlib.Path(__file__).resolve().parent.parent.parent
