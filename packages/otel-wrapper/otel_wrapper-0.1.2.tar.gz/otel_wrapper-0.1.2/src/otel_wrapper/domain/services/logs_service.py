from ...infrastructure.ports.outbound_logs_exporter import iLogsExporter


class LogsProcessorService:
    def __init__(self, log_exporter: iLogsExporter):
        self._exporter = log_exporter

    def new_log(self, msg: str, tags: dict, level: int):
        logger = self._exporter.get_logger()
        logger.log(level, msg, extra=tags)

    def get_logger(self):
        return self._exporter.get_logger()
