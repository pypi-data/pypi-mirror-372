import json
import sys

if __name__ == "__main__":
    """
    This is a developer utility to detect possible regressions in changes that have been made. To use, first
    run the harness twice. One with an older copy of this repo containing a known-good state and another that
    includes your changes.

    Make note of the output folder locations for each run.

    Then run: pdm run regression_detector <path_to_old_harness_output> <path_to_new_harness_output> [--git, --jira]

    This will compare the two outputs and detect notable differences.
    """
    # Note - git regression detection not implemented yet
    include_git = '--git' in sys.argv
    include_jira = '--jira' in sys.argv

    try:
        orig_dir = sys.argv[1]
        changes_dir = sys.argv[2]
    except IndexError:
        print("Please provide two directories to compare.")
        exit(1)

    if include_jira:
        orig_jira_ids = set()
        new_jira_ids = set()

        # Right now this only does one check: compare the issue count of downloaded jira ids and ensure they're close.
        try:
            with open(f"{orig_dir}/jira/jira_issue_ids_downloaded.json", "r") as f:
                id_lines = f.readlines()
                for i in id_lines:
                    orig_jira_ids.add(i.strip('\n \t ,'))

            with open(f"{changes_dir}/jira/jira_issue_ids_downloaded.json", "r") as f:
                id_lines = f.readlines()
                for i in id_lines:
                    new_jira_ids.add(i.strip('\n \t ,'))
        except FileNotFoundError:
            print("File(s) containing Jira issue ids not found.")
            exit(1)

        # We expect a few tickets to have been added or removed between runs,
        # but let's say 10 is the threshold which warrants investigation.
        if abs(len(orig_jira_ids) - len(new_jira_ids)) > 10:
            print(f"Jira issue count mismatch: {len(orig_jira_ids)} vs {len(new_jira_ids)}")
            print(f"Issues in original that appear gone: {orig_jira_ids - new_jira_ids}")
            print(f"Issues in new that did not exist before: {new_jira_ids - orig_jira_ids}")

            exit(1)

        # Check that number of users is close
        try:
            with open(f"{orig_dir}/jira/jira_users.json", "r") as f:
                data = json.load(f)
                old_user_count = len(data)

            with open(f"{changes_dir}/jira/jira_users.json", "r") as f:
                data = json.load(f)
                new_user_count = len(data)
        except FileNotFoundError:
            print("File(s) containing Jira users not found.")
            exit(1)

        if abs(old_user_count - new_user_count) > 10:
            print(f"Jira user count mismatch: {old_user_count} vs {new_user_count}")
            exit(2)

    print("No issues detected.")
    exit(0)
