import os

import requests
from IPython import get_ipython
from IPython.core.magic import magics_class, Magics, line_magic


@magics_class
class FinanceBotMagics(Magics):

    @property
    def finb_server_url(self):
        return os.environ["FINB_SERVER_URL"]


def load_ipython_extension(ipython):
    ipython.register_magics(FinanceBotMagics)
