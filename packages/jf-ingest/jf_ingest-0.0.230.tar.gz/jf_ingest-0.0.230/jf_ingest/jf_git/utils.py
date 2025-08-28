import re
from functools import wraps
from typing import List

from jf_ingest.name_redactor import NameRedactor

branch_redactor = NameRedactor(preserve_names=['master', 'develop'])
organization_redactor = NameRedactor()
repo_redactor = NameRedactor()


def sanitize_text(text: str) -> str:
    """Helper function for removing everything other than jira keys out of
    text bodies

    Args:
        text (str): A given string to "sanitize"

    Returns:
        str: The inputted text str, but with any Jira Key purged out of it
    """
    # NOTE: This module is used only by git, but we need to clean up Jira
    # keys out of commit messages. That's what this regex is for
    JIRA_KEY_REGEX = re.compile(r'([a-z0-9]+)[-|_|/| ]?(\d+)', re.IGNORECASE)

    if not text:
        return text

    regex_matches: List[str] = JIRA_KEY_REGEX.findall(text)

    return (' ').join(
        {f'{match[0].upper().strip()}-{match[1].upper().strip()}' for match in regex_matches}
    )
