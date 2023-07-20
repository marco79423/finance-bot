import abc

from sqlalchemy.dialects.mysql import insert


class UpdaterBase(abc.ABC):
    def __init__(self, session):
        self.session = session

    def save_or_update(self, model, data):
        insert_stmt = insert(model).values(**data).on_duplicate_key_update(**data)
        self.session.execute(insert_stmt)

    def save_or_update_list(self, model, data_list):
        insert_stmts = []
        for data in data_list:
            insert_stmt = insert(model).values(**data).on_duplicate_key_update(**data)
            insert_stmts.append(insert_stmt)
        self.session.execute(insert_stmts)
