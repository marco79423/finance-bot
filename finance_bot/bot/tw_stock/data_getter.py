from .stock_getter import StockGetter


class DataGetter:

    def __getitem__(self, stock_id):
        return StockGetter(stock_id)
