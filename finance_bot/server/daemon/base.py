import abc


class DaemonBase:
    def __init__(self, app):
        self._app = app

    @abc.abstractmethod
    def start(self):
        pass

    @property
    def app(self):
        return self._app

    @property
    def config(self):
        return self._app.state.config

    @property
    def logger(self):
        return self._app.state.logger

    @property
    def scheduler(self):
        return self._app.state.scheduler
