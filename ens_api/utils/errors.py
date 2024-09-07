class ResolutionFailed(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class WrongResolverUsed(Exception):
    def __init__(self, message=None):
        super().__init__(message)
