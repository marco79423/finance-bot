import pandas as pd

from finance_bot.infrastructure.base import ManagerBase


class DatabaseCacheManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)

    def save(self, key, df):
        df.to_pickle(self.infra.path.db_cache_folder / (key + '.pkl'))

    def read(self, key, **kargs):
        return pd.read_pickle(self.infra.path.db_cache_folder / (key + '.pkl'), **kargs)
