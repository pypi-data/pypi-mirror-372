import re
from typing import Optional


class NameRedactor:
    """This is a helper class for cleaning up sensitive data that gets submitted
    by the agent. It is currently only used by the Git ingest functionality.

    The boolean fields related to this logic are found on the GitConfig. They are:
        GitConfig.git_strip_text_content,
        GitConfig.git_redact_names_and_urls,
    """

    def __init__(self, preserve_names: Optional[list[str]] = None) -> None:
        self.redacted_names: dict[str, str] = {}
        self.seq = 0
        self.preserve_names: list[str] = preserve_names or []

    def redact_name(self, name: Optional[str]) -> Optional[str]:
        if not name or name in self.preserve_names:
            return name

        redacted_name = self.redacted_names.get(name)

        # Check to see if name is already redacted
        if re.match('redacted-\d\d\d\d', name):
            redacted_name = name

        if not redacted_name:
            redacted_name = f'redacted-{self.seq:04}'
            self.seq += 1
            self.redacted_names[name] = redacted_name
        return redacted_name
