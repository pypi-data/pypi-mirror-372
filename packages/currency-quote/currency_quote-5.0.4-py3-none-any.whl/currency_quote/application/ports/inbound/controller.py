from abc import ABC, abstractmethod


class IController(ABC):
    @abstractmethod
    def __init__(self, currency_list: list):
        pass

    @abstractmethod
    def get_last_quote(self) -> dict:
        pass

    @abstractmethod
    def get_history_quote(self, reference_date: int) -> dict:
        pass
