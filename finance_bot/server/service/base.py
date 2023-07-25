import abc


class ServiceBase:
    name = 'service_base'

    def __init__(self, app):
        app.state.service[self.name] = self
        self.app = app
        self.logger = app.state.logger.getChild(self.name)

    def start(self):
        self.logger.info(f'啟動 {self.name} 功能...')
        self.set_schedules()

    @abc.abstractmethod
    def set_schedules(self):
        pass

    @property
    def config(self):
        return self.app.state.config

    @property
    def scheduler(self):
        return self.app.state.scheduler
