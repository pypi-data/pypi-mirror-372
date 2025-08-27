# NOTE: These should be python objects, assuming that we've already parsed the JSON or received objects.
raw_get_pr_gql = [
    {
        "id": "gid://gitlab/MergeRequest/12345",
        "diffStatsSummary": {
            "additions": 9,
            "deletions": 2,
            "fileCount": 1
        },
        "diffStats": [
            {
                "additions": 9,
                "deletions": 2,
                "path": "metadata/test.yml"
            }
        ],
        "closedAt": None,
        "updatedAt": "2025-01-08T05:45:50Z",
        "mergedAt": "2025-01-08T05:45:48Z",
        "createdAt": "2025-01-08T05:34:00Z",
        "title": "Example PR",
        "description": "This is an example PR description",
        "webUrl": "https://gitlab.com/example/path/-/merge_requests/12345",
        "sourceBranch": "test_source",
        "targetBranch": "master",
        "author": {
            "id": "gid://gitlab/User/12345",
            "name": "Example User",
            "username": "example_user",
            "webUrl": "https://gitlab.com/example-user",
            "publicEmail": "exampleuser@example.com"
        },
        "mergeUser": {
            "id": "gid://gitlab/User/12345",
            "name": "Example User",
            "username": "example_user",
            "webUrl": "https://gitlab.com/example-user",
            "publicEmail": "exampleuser@example.com"
        },
        "commits": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MQ"
            },
            "nodes": [
                {
                    "id": "gid://gitlab/Commit/17e1fe4512a1493be6d4a3363467a946f4b8f737",
                    "sha": "9fafae5b36b201422c44205174efe9e8033ad224",
                    "webUrl": "https://gitlab.com/example/path/-/commit/9fbfae5b36b201422c44205174fee9e8033ad224",
                    "message": "Example Commit",
                    "committedDate": "2025-01-08T05:33:58Z",
                    "authoredDate": "2025-01-08T05:33:58Z",
                    "author": None
                }
            ]
        },
        "mergeCommitSha": None,
        "notes": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MQ"
            },
            "nodes": [
                {
                    "id": "gid://gitlab/Note/2342819393",
                    "body": "Example system note",
                    "createdAt": "2025-01-08T05:34:17Z",
                    "system": True,
                    "author": {
                        "id": "gid://gitlab/User/12346",
                        "name": "Example Bot",
                        "username": "Example Bot",
                        "webUrl": "https://gitlab.com/example-bot",
                        "publicEmail": ""
                    }
                }
            ]
         },
        "approvedBy": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MQ"
            },
            "nodes": []
        },
        "sourceProject": {
            "id": "gid://gitlab/Project/12135",
            "name": "test_source",
            "webUrl": "https://gitlab.com/gitlab-org/gitlab"
        },
        "targetProject": {
            "id": "gid://gitlab/Project/51313",
            "name": "test_target",
            "webUrl": "https://gitlab.com/gitlab-org/gitlab"
        }
    },
    {
      "id": "gid://gitlab/MergeRequest/54321",
      "diffStatsSummary": {
        "additions": 1,
        "deletions": 1,
        "fileCount": 1
      },
      "diffStats": [
        {
          "additions": 1,
          "deletions": 1,
          "path": "doc/editor_extensions/visual_studio_code/troubleshooting.md"
        }
      ],
      "closedAt": None,
      "updatedAt": "2025-01-08T17:33:41Z",
      "mergedAt": None,
      "createdAt": "2025-01-08T17:27:30Z",
      "title": "Updating commands to latest",
      "description": "Example Description",
      "webUrl": "https://gitlab.com/gitlab-org/gitlab/-/merge_requests/123456789",
      "sourceBranch": "master-patch",
      "targetBranch": "master",
      "author": {
        "id": "gid://gitlab/User/54321",
        "name": "Person Example",
        "username": "personexample",
        "webUrl": "https://gitlab.com/person",
        "publicEmail": ""
      },
      "mergeUser": None,
      "commits": {
          "pageInfo": {
              "hasNextPage": False,
              "endCursor": "MQ"
          },
        "nodes": [
          {
            "id": "gid://gitlab/Commit/f7e1fe4512a1493be6d4a4363467a6f4b8f733",
            "sha": "3d225cvbf347e8941b6e5f16947c5b9a4ec19fz5",
            "webUrl": "https://gitlab.com/gitlab-org/gitlab/-/commit/4z225c2bf347e8940b6e5f36947c5h9a4ec19fc5",
            "message": "Updating commands",
            "committedDate": "2025-01-08T17:26:52Z",
            "authoredDate": "2025-01-08T17:26:52Z",
            "author": {
              "id": "gid://gitlab/User/54321",
              "name": "Person Example",
              "username": "personexample",
              "webUrl": "https://gitlab.com/person",
              "publicEmail": ""
            }
          }
        ]
      },
      "mergeCommitSha": None,
      "notes": {
          "pageInfo": {
              "hasNextPage": False,
              "endCursor": "MQ"
          },
          "nodes": [
                {
                  "id": "gid://gitlab/Note/3342812391",
                  "body": "assigned to @person",
                  "createdAt": "2025-01-08T17:27:31Z",
                  "system": True,
                  "author": {
                    "id": "gid://gitlab/User/54321",
                    "name": "Person Example",
                    "username": "personexample",
                    "webUrl": "https://gitlab.com/person",
                    "publicEmail": ""
                  }
                },
                {
                  "id": "gid://gitlab/Note/3342812392",
                  "body": "requested review from @person",
                  "createdAt": "2025-01-08T17:28:45Z",
                  "system": True,
                  "author": {
                    "id": "gid://gitlab/User/5213246",
                    "name": "Person Note",
                    "username": "person",
                    "webUrl": "https://gitlab.com/person",
                    "publicEmail": ""
                  }
                },
                {
                "id": "gid://gitlab/Note/3342812393",
                  "body": "Test Note",
                  "createdAt": "2025-01-08T17:29:45Z",
                  "system": False,
                  "author": {
                    "id": "gid://gitlab/User/54231",
                    "name": "****",
                    "username": "private_user",
                    "webUrl": "https://gitlab.com/private_user",
                    "publicEmail": None
                  }
                }
              ]
      },
      "approvedBy": {
          "pageInfo": {
              "hasNextPage": False,
              "endCursor": "MQ"
          },
        "nodes": [
          {
            "id": "gid://gitlab/User/543215",
            "name": "Person Example2",
            "username": "personexample2",
            "webUrl": "https://gitlab.com/person2",
            "publicEmail": ""
          }
        ]
      },
      "sourceProject": {
        "id": "gid://gitlab/Project/12345",
        "name": "GitLab",
        "webUrl": "https://gitlab.com/gitlab-org/gitlab"
      },
      "targetProject": {
        "id": "gid://gitlab/Project/54321",
        "name": "GitLab",
        "webUrl": "https://gitlab.com/gitlab-org/gitlab"
      }
    }
]