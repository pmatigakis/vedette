class ApiError(Exception):
    pass


class InvalidProjectPublicKey(ApiError):
    pass


class InvalidEventData(ApiError):
    pass


class EventAlreadyProcessed(ApiError):
    pass
