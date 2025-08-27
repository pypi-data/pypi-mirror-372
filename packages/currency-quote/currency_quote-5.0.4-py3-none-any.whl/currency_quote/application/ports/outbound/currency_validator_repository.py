# src/currency_quote/application/ports/outbound/currency_validator_port.py
from abc import ABC, abstractmethod
from currency_quote.domain.entities.currency import CurrencyQuote


class ICurrencyValidator(ABC):
    @abstractmethod
    def __init__(self, currency_quote: CurrencyQuote):
        pass

    @abstractmethod
    def validate_currency_code(self) -> list:
        pass
