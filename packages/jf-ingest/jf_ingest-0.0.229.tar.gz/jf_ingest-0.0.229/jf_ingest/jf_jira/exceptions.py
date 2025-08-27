class JiraRetryLimitExceeded(Exception):
    pass


class NoAccessibleProjectsException(Exception):
    pass


class NoJiraUsersFoundException(Exception):
    pass


class AtlassianConnectException(Exception):
    pass
