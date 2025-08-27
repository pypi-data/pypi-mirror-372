# src/currency_quote/adapters/outbound/currency_validator_api.py
from api_to_dataframe import ClientBuilder, RetryStrategies
from currency_quote.config.endpoints import API
from currency_quote.application.ports.outbound.currency_validator_repository import (
    ICurrencyValidator,
)
from currency_quote.domain.entities.currency import CurrencyObject


class CurrencyValidatorAPI(ICurrencyValidator):
    def __init__(self, currency_quote: CurrencyObject) -> None:
        self.currency_quote = currency_quote

    def validate_currency_code(self) -> list:
        client = ClientBuilder(
            endpoint=API.ENDPOINT_AVALIABLE_PARITIES,
            retry_strategy=RetryStrategies.LINEAR_RETRY_STRATEGY,
        )

        valid_list = client.get_api_data()

        validated_list = []

        for currency_code in self.currency_quote.get_currency_list():
            if currency_code in valid_list:
                validated_list.append(currency_code)

        return validated_list
