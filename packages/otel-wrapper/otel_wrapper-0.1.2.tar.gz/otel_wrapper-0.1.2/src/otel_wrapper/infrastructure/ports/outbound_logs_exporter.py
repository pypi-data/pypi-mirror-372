import logging
from abc import ABC, abstractmethod


class iLogsExporter(ABC):
    @abstractmethod
    def get_logger(self) -> logging.RootLogger:
        pass
