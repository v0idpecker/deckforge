class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    pass


class InvalidInputError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class MultipleResultsError(ServiceError):
    pass


class DataAccessError(ServiceError):
    pass
