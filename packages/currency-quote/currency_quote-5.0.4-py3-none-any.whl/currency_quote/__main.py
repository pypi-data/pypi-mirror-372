from currency_quote import ClientBuilder

# For get the last quote of one currency
# client = ClientBuilder(currency_list="USD-BRL")
# or get quotes of multiple currencies
#
client = ClientBuilder(currency_list=["EUR-BRL"])
#
# # Get the last quote
print(client.get_last_quote())
# # Get history quote of currency
print(client.get_history_quote(reference_date=20240626))
