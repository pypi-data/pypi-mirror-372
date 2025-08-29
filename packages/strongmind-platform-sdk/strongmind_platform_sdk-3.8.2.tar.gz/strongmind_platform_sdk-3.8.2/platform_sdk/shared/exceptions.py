from requests import HTTPError

ID_MAPPER_DEPENDENCY_NAME = 'IdMapper'


class IdentifierMapperError(Exception):
    """A generic error class when we get an error from Identifier Mapper."""
    dependency_name = ID_MAPPER_DEPENDENCY_NAME

    def __init__(self, http_error: HTTPError = None):
        if http_error:
            self.request = http_error.request
            self.response = http_error.response


class PairNotFoundError(IdentifierMapperError):
    """A Pair is not found in the Identifier Mapper"""


class PartnerNotFoundError(IdentifierMapperError):
    """A Partner could not found in the Identifier Mapper"""
