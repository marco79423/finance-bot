import abc


class UpdaterBase(abc.ABC):
    def __init__(self, session):
        self.session = session
