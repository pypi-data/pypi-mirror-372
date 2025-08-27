# currency-quote-wrapper: Complete solution for extracting currency pair quotes data.

## Project description
Complete solution for extracting currency pair quotes data.
With comprehensive testing, parameter validation, flexible configuration management, Hexagonal Architecture, CI/CD pipelines, code quality tools, and detailed documentation.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ivanildobarauna-dev/currency-quote)

[![PyPI - Status](https://img.shields.io/pypi/status/currency-quote?style=for-the-badge&logo=pypi)](https://pypi.org/project/currency-quote/)

[![PyPI - Downloads](https://img.shields.io/pypi/dm/currency-quote?style=for-the-badge&logo=pypi)](https://pypi.org/project/currency-quote/)

[![PyPI - Version](https://img.shields.io/pypi/v/currency-quote?style=for-the-badge&logo=pypi)](https://pypi.org/project/currency-quote/#history)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/currency-quote?style=for-the-badge&logo=python)

[![CI](https://img.shields.io/github/actions/workflow/status/ivdatahub/currency-quote/CI.yaml?&style=for-the-badge&logo=githubactions&cacheSeconds=60&label=Tests+and+pre+build)](https://github.com/ivdatahub/currency-quote/actions/workflows/CI.yaml)
[![CD](https://img.shields.io/github/actions/workflow/status/ivdatahub/currency-quote/CD.yaml?&style=for-the-badge&logo=githubactions&cacheSeconds=60&event=release&label=Package+publication)](https://github.com/ivdatahub/currency-quote/actions/workflows/CD.yaml)

[![Codecov](https://img.shields.io/codecov/c/github/ivdatahub/currency-quote?style=for-the-badge&logo=codecov)](https://app.codecov.io/gh/ivdatahub/currency-quote)

## Project Stack

![Python](https://img.shields.io/badge/-Python-05122A?style=flat&logo=python)&nbsp;
![Docker](https://img.shields.io/badge/-Docker-05122A?style=flat&logo=docker)&nbsp;
![Poetry](https://img.shields.io/badge/-Poetry-05122A?style=flat&logo=poetry)&nbsp;
![GitHub Actions](https://img.shields.io/badge/-GitHub_Actions-05122A?style=flat&logo=githubactions)&nbsp;
![CodeCov](https://img.shields.io/badge/-CodeCov-05122A?style=flat&logo=codecov)&nbsp;
![pypi](https://img.shields.io/badge/-pypi-05122A?style=flat&logo=pypi)&nbsp;
![pandas](https://img.shields.io/badge/-pandas-05122A?style=flat&logo=pandas)&nbsp;
![pytest](https://img.shields.io/badge/-pytest-05122A?style=flat&logo=pytest)&nbsp;


## Project Highlights:

- **Comprehensive Testing:** Development of tests to ensure the quality and robustness of the code

- **Parameter Validation:** Sending valid parameters based on the request data source itself, ensuring the integrity and accuracy of the information processed.

- **Configuration Management:** Use of a configuration module to manage endpoints, retry times and number of attempts, providing flexibility and ease of adjustment.

- **Hexagonal Architecture:** Adoption of Hexagonal Architecture to decouple the core logic from external dependencies, ensuring that any current data source can be replaced seamlessly in case of unavailability. This is facilitated by the use of adapters, which act as intermediaries between the core application and the external services.

- **Cotinuous Integration** and Continuous Deployment: Use of CI/CD pipelines to automate the build, test and deployment processes, ensuring that the application is always up to date and ready for use.

- **Code Quality:** Use of code quality tools such as linters and formatters to ensure that the codebase is clean, consistent and easy to read.

- **Documentation:** Creation of detailed documentation to facilitate the understanding and use of the application, including installation instructions, usage examples and troubleshooting guides.

## Contributing

See the following docs:

- [Contributing Guide](https://github.com/ivdatahub/currency-quote-wrapper/blob/main/CONTRIBUTING.md)
- [Code Of Conduct](https://github.com/ivdatahub/currency-quote/blob/main/CODE_OF_CONDUCT.md)


## How to get currency quotes using this library

``` python
## Importing library
from currency_quote import ClientBuilder

# For get the last quote of one currency
client = ClientBuilder(currency_list="USD-BRL")
# or get quotes of multiple currencies
client = ClientBuilder(currency_list=['USD-BRL', 'EUR-BRL'])

# Get the last quote
print(client.get_last_quote())
# Get history quote of currency
print(client.get_history_quote(reference_date=20220101))
```
* This is expected payload for get Last Quote with USD-BRL currency pair
```json
[
   {
      "currency_pair":"USD-BRL",
      "currency_pair_name":"Dólar Americano/Real Brasileiro",
      "base_currency_code":"USD",
      "quote_currency_code":"BRL",
      "quote_timestamp":1727201744,
      "bid_price":"5.4579",
      "ask_price":"5.4589",
      "quote_extracted_at":1727201753
   }
]
```

* This is expected payload for get History Quote with USD-BRL currency pair

```json
[
   {
      "currency_pair":"USD-BRL",
      "currency_pair_name":"Dólar Americano/Real Brasileiro",
      "base_currency_code":"USD",
      "quote_currency_code":"BRL",
      "quote_timestamp":1719440767,
      "bid_price":5.524,
      "ask_price":5.5245,
      "quote_extracted_at":1727201753
   }
]
```

* This is expected payload for get last Quote with two or more currencies

```json
[
   {
      "currency_pair":"USD-BRL",
      "currency_pair_name":"Dólar Americano/Real Brasileiro",
      "base_currency_code":"USD",
      "quote_currency_code":"BRL",
      "quote_timestamp":1727201384,
      "bid_price":"5.4594",
      "ask_price":"5.4599",
      "quote_extracted_at":1727201387
   },
   {
      "currency_pair":"USD-EUR",
      "currency_pair_name":"Dólar Americano/Euro",
      "base_currency_code":"USD",
      "quote_currency_code":"EUR",
      "quote_timestamp":1727201376,
      "bid_price":"0.8957",
      "ask_price":"0.8958",
      "quote_extracted_at":1727201387
   }
]
```
* This is expected payload for history last Quote with two or more currencies
```json
[
   {
      "currency_pair":"USD-BRL",
      "currency_pair_name":"Dólar Americano/Real Brasileiro",
      "base_currency_code":"USD",
      "quote_currency_code":"BRL",
      "quote_timestamp":1727201384,
      "bid_price":"5.4594",
      "ask_price":"5.4599",
      "quote_extracted_at":1727201387
   },
   {
      "currency_pair":"USD-EUR",
      "currency_pair_name":"Dólar Americano/Euro",
      "base_currency_code":"USD",
      "quote_currency_code":"EUR",
      "quote_timestamp":1727201376,
      "bid_price":"0.8957",
      "ask_price":"0.8958",
      "quote_extracted_at":1727201387
   }
]
```
## Hexagonal Design of library

![Arch](./hexagonal_design_arch.png)

