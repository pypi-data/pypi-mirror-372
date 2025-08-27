# src/currency_quote/application/use_cases/validate_currency.py
from typing import List
from currency_quote.adapters.outbound.currency_api import CurrencyAPI
from currency_quote.domain.services.get_currency_quote import GetCurrencyQuoteService
from currency_quote.domain.entities.currency import CurrencyObject, CurrencyQuote


class GetHistCurrencyQuoteUseCase:
    @staticmethod
    def execute(
        currency_obj: CurrencyObject, reference_date: int
    ) -> List[CurrencyQuote]:
        quote_service = GetCurrencyQuoteService(
            currency=currency_obj, currency_repository=CurrencyAPI
        )
        return quote_service.history(reference_date=reference_date)
