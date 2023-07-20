import os

import requests
from IPython import get_ipython
from IPython.core.magic import magics_class, Magics, line_magic


@magics_class
class FinanceBotMagics(Magics):

    @line_magic
    def lending(self, line: str):
        if line.strip() == 'records':
            try:
                resp = requests.get(f'{self.finb_server_url}/lending/records')
                records = resp.json()
                return sorted(records, key=lambda r: r['end'])
            except requests.exceptions.RequestException:
                print(f'理財機器人 ({self.finb_server_url}) 連線失敗')

    @property
    def finb_server_url(self):
        return os.environ["FINB_SERVER_URL"]


def load_ipython_extension(ipython):
    ipython.register_magics(FinanceBotMagics)
