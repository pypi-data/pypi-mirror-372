import uuid

import pytest

from allspice import AllSpice, Issue

# put a ".token" file into your directory containg only the token for AllSpice Hub


@pytest.fixture(scope="session")
def port(pytestconfig):
    """Load --port command-line arg if set"""
    return pytestconfig.getoption("port")


@pytest.fixture
def instance(port, scope="module"):
    try:
        g = AllSpice(
            f"http://localhost:{port}", open(".token", "r").read().strip(), ratelimiting=None
        )
        print("AllSpice Hub Version: " + g.get_version())
        print("API-Token belongs to user: " + g.get_user().username)
        return g
    except Exception:
        assert False, (
            f"AllSpice Hub could not load. \
                - Instance running at http://localhost:{port} \
                - Token at .token   \
                    ?"
        )


# make up some fresh names for the tests run
test_org = "org_" + uuid.uuid4().hex[:8]
test_user = "user_" + uuid.uuid4().hex[:8]
test_team = "team_" + uuid.uuid4().hex[:8]  # team names seem to have a rather low max length
test_repo = "repo_" + uuid.uuid4().hex[:8]


def _create_test_org(instance, test_name):
    test_user_unique = "-".join([test_user, test_name])
    user = instance.create_user(
        test_user_unique, test_user_unique + "@example.org", "abcdefg1.23AB", send_notify=False
    )
    return instance.create_org(
        user, "-".join([test_org, test_name]), "some Description for longtests"
    )


def test_list_repos(request, instance):
    org = _create_test_org(instance, request.node.name)
    repos = org.get_repositories()
    assert len(repos) == 0
    # test a number of repository listings larger than the pagination number (default 50)
    for i in range(1, 54):
        instance.create_repo(org, test_repo + "_" + str(i), str(i))
    repos = org.get_repositories()
    assert len(repos) >= 53


def test_list_issue(request, instance):
    org = _create_test_org(instance, request.node.name)
    repo = instance.create_repo(
        org, test_repo, "Testing a huge number of Issues and how they are listed"
    )
    for x in range(0, 100):
        Issue.create_issue(
            instance, repo, "TestIssue" + str(x), "We will be too many to be listed on one page"
        )
    issues = repo.get_issues()
    assert len(issues) > 98


def test_list_team_members(request, instance):
    org = _create_test_org(instance, request.node.name)

    team = org.create_team(test_team, "Team for longtests")
    users = []
    for i in range(100):
        users.append(
            instance.create_user(
                test_user + str(i),
                test_user + str(i) + "@example.org",
                "abcdefg1.23AB",
                send_notify=False,
            ),
        )
    for user in users:
        team.add_user(user)
    assert len(team.get_members()) == len(users)
