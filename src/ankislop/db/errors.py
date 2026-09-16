class DAOError(Exception):
    pass


class DAONotFoundError(DAOError):
    pass


class DAOInvalidInputError(DAOError):
    pass


class DAOMultipleResultsError(DAOError):
    pass


class DAOIntegrityError(DAOError):
    pass
