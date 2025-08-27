from .deps_injector import wrapper_builder
from .builder import Wrapper


class OpenObservability:
    def __init__(self, application_name: str):
        self._wrapper = wrapper_builder(application_name=application_name)

    def get_wrapper(self) -> Wrapper:
        return self._wrapper


__all__ = [OpenObservability]
