from currency_quote.adapters.inbound.lib_controller import ClientBuilder
from currency_quote.utils.logger import setup_logging

# Setup logging when package is imported
setup_logging()

__all__ = ["ClientBuilder"]
