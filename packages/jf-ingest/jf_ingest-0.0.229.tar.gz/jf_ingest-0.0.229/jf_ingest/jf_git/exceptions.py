from typing import Optional


class GitProviderUnavailable(Exception):
    pass


class GqlRateLimitExceededException(Exception):
    pass


class GqlPageTimeoutException(Exception):
    pass


class GitAuthenticationException(Exception):
    def __init__(self, *args, original_exception: Optional[Exception] = None):
        self.original_exception = original_exception
        super().__init__(*args)


class GitAuthorizationException(Exception):
    pass
