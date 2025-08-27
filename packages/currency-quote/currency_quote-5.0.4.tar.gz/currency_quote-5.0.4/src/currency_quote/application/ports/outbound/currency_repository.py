# src/currency_quote/application/ports/outbound/currency_validator_port.py
from abc import ABC, abstractmethod
from typing import List
from currency_quote.domain.entities.currency import CurrencyQuote, CurrencyObject


class ICurrencyRepository(ABC):
    @abstractmethod
    def __init__(self, currency_obj: CurrencyObject):
        pass

    @abstractmethod
    def get_last_quote(self) -> List[CurrencyQuote]:
        pass

    @abstractmethod
    def get_history_quote(self, reference_date: int) -> List[CurrencyQuote]:
        pass
