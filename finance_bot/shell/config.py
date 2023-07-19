from traitlets.config import Config


def get_config(url):
    c = Config()
    c.InteractiveShellApp.exec_lines = [
        # 重要套件
        'import numpy as np',
        'import pandas as pd',

        # 環境變數
        f'FINB_SERVER_URL={url}'
    ]
    c.InteractiveShellApp.extensions = [
        'finance_bot.shell.extension'
    ]
    c.InteractiveShell.colors = 'LightBG'
    c.InteractiveShell.confirm_exit = False
    c.TerminalIPythonApp.display_banner = False
    return c
