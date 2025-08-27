class API:
    __URL__ = "https://economia.awesomeapi.com.br"
    ENDPOINT_AVALIABLE_PARITIES = __URL__ + "/json/available"
    ENDPOINT_LAST_COTATION = __URL__ + "/last/"
    ENDPOINT_HISTORY_COTATION = __URL__ + "/json/daily/"
    RETRY_TIME_SECONDS = 2
    RETRY_ATTEMPTS = 3
