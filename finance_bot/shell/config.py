from traitlets.config import Config


def get_config(url):
    c = Config()
    c.InteractiveShellApp.exec_lines = [
        # 重要套件
        'import os',
        'import numpy as np',
        'import pandas as pd',

        # 環境變數
        f'os.environ["FINB_SERVER_URL"]="{url}"',

        # 重要設定
        'pd.set_option("plotting.backend", "plotly")',
    ]
    c.InteractiveShellApp.extensions = [
        'finance_bot.shell.extension'
    ]
    c.InteractiveShell.colors = 'LightBG'
    c.InteractiveShell.confirm_exit = False
    c.InteractiveShell.banner1 = '理財機器人 Shell'
    c.InteractiveShell.banner2 = f'Server: {url}'
    return c
