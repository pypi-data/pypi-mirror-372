class Constants:
    JELLYFISH_USER_AGENT = f'jellyfish/1.0'
    GITLAB_PUBLIC_HOSTNAME = 'gitlab.com'
    # This is how many bytes are in a MB. This is used when
    # determining how much data to upload to S3 (we generally)
    # batch files by ~50 MBs
    MB_SIZE_IN_BYTES = 1048576
    JIRA_ISSUES_UNCOMPRESSED_FILE_SIZE = 50 * MB_SIZE_IN_BYTES
    # When inserting JiraIssues to our database we cannot handle
    # any issue that is stringified and larger than 255 MBs
    JIRA_ISSUE_SIZE_LIMIT = 255 * MB_SIZE_IN_BYTES
    # 250 is the default largest value we can pull from Jira Server
    # For cloud it's 100, but we have logic to check what Jira
    # limits us to and reduce our batch size to that
    MAX_ISSUE_API_BATCH_SIZE = 250
    # Uses a pull-by-id approach to fetching sprints
    PULL_SPRINTS_BY_ID = 'makara-pull-sprints-by-id-2024Q4'
    # Flags control how many workers to use when threading for pulling sprints by board or by id
    PULL_SPRINTS_BY_ID_MAX_WORKERS = 'makara-pull-sprints-by-id-max-workers-2025Q1'
    PULL_SPRINTS_BY_BOARD_MAX_WORKERS = 'makara-pull-sprints-by-board-max-workers-2025Q1'
    PULL_SPRINTS_SKIP_INACTIVE = 'makara-pull-sprints-skip-inactive-2025Q1'
    # Flag for if we should crawl across all our issues and pull additional users we detect
    CHECK_ISSUES_FOR_EXTRA_USERS_AND_PULL = 'makara-check-for-extra-users-in-issues-2025Q2'
    # Feature flag for JQL Enhanced Search API migration
    JQL_ENHANCED_SEARCH_ENABLED = 'makara-jql-enhanced-search-enabled-2025Q3'
    # Feature flag to force legacy API for troubleshooting
    FORCE_LEGACY_API = 'makara-force-legacy-api-2025Q3'
