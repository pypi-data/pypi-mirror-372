import base64
import datetime
import time
import uuid

import pytest

from allspice import (
    AllSpice,
    Branch,
    Comment,
    DesignReview,
    DesignReviewReview,
    Issue,
    Milestone,
    NotFoundException,
    Organization,
    Repository,
    Team,
    User,
)
from allspice.apiobject import CommitStatusState, Util
from allspice.exceptions import NotYetGeneratedException
from allspice.utils.retry_generated import retry_not_yet_generated

# put a ".token" file into your directory containg only the token for AllSpice Hub


@pytest.fixture(scope="session")
def port(pytestconfig):
    """Load --port command-line arg if set"""
    return pytestconfig.getoption("port")


@pytest.fixture
def instance(port, scope="module"):
    try:
        g = AllSpice(
            f"http://localhost:{port}",
            open(".token", "r").read().strip(),
            ratelimiting=None,
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
test_team = "team_" + uuid.uuid4().hex[:8]  # team names seem to have a rather low max lenght
test_repo = "repo_" + uuid.uuid4().hex[:8]
# Topic names can't have underscores.
test_topic = "topic-" + uuid.uuid4().hex[:8]


def test_token_owner(instance):
    user = instance.get_user()
    assert user.username == "test", "Token user not 'tests'."
    assert user.is_admin, "Testuser is not Admin - Tests may fail"


def test_allspice_hub_version(instance):
    assert instance.get_version().startswith("1."), "No Version String returned"


def test_fail_get_non_existent_user(instance):
    with pytest.raises(NotFoundException):
        User.request(instance, test_user)


def test_fail_get_non_existent_org(instance):
    with pytest.raises(NotFoundException):
        Organization.request(instance, test_org)


def test_fail_get_non_existent_repo(instance):
    with pytest.raises(NotFoundException):
        Repository.request(instance, test_user, test_repo)


def test_create_user(instance):
    email = test_user + "@example.org"
    user = instance.create_user(test_user, email, "abcdefg1.23AB", send_notify=False)
    assert user.username == test_user
    assert user.login == test_user
    assert email in user.emails
    assert user.email == email
    assert not user.is_admin
    assert isinstance(user.id, int)
    assert user.is_admin is False


def test_change_user(instance):
    user = instance.get_user_by_name(test_user)
    location = "a house"
    user.location = location
    new_fullname = "Other Test Full Name"
    user.full_name = new_fullname
    user.commit(user.username, 0)
    del user
    user = instance.get_user_by_name(test_user)
    assert user.full_name == new_fullname
    assert user.location == location


def test_create_org(instance):
    user = instance.get_user()
    org = instance.create_org(user, test_org, "some-desc", "loc")
    assert org.get_members()[0] == user
    assert org.description == "some-desc"
    assert org.username == test_org
    assert org.location == "loc"
    assert not org.website
    assert not org.full_name


def test_non_changable_field(instance):
    org = Organization.request(instance, test_org)
    with pytest.raises(AttributeError):
        org.id = 55


def test_create_repo_userowned(instance):
    org = User.request(instance, test_user)
    repo = instance.create_repo(org, test_repo, "user owned repo")
    assert repo.description == "user owned repo"
    assert repo.owner == org
    assert repo.name == test_repo
    assert not repo.private


def test_edit_org_fields_and_commit(instance):
    org = Organization.request(instance, test_org)
    org.description = "some thing other man"
    org.location = "somewehre new"
    org.visibility = "public"
    org.website = "http:\\\\testurl.com"
    org.commit()
    org2 = Organization.request(instance, test_org)
    assert org2.name == test_org
    assert org2.description == "some thing other man"
    assert org2.location == "somewehre new"
    # assert org2.visibility == "private" # after commiting, this field just vanishes (Bug?)
    assert org2.website == "http:\\\\testurl.com"


def test_create_repo_orgowned(instance):
    org = Organization.request(instance, test_org)
    repo = instance.create_repo(org, test_repo, "descr")
    assert repo.description == "descr"
    assert repo.owner == org
    assert repo.name == test_repo
    assert not repo.private


def test_get_repository(instance):
    repo = instance.get_repository(test_org, test_repo)
    assert repo is not None
    assert repo.name == test_repo
    assert repo.owner.username == test_org


def test_add_content_to_repo(instance):
    repo = Repository.request(instance, test_org, test_repo)
    file_content = open("tests/data/test.pcbdoc", "rb").read()
    file_content = base64.b64encode(file_content).decode("utf-8")
    repo.create_file("test.pcbdoc", file_content)
    assert len(repo.get_commits()) == 2
    assert [content.name for content in repo.get_git_content()] == [
        "README.md",
        "test.pcbdoc",
    ]


def test_get_repo_tree(instance):
    repo = Repository.request(instance, test_org, test_repo)
    tree = repo.get_tree()
    assert len(tree) == 2
    assert tree[0].path == "README.md"


def test_get_json_before_generated(instance):
    repo = Repository.request(instance, test_org, test_repo)
    with pytest.raises(NotYetGeneratedException):
        repo.get_generated_json("test.pcbdoc")


def test_get_svg_before_generated(instance):
    repo = Repository.request(instance, test_org, test_repo)
    with pytest.raises(NotYetGeneratedException):
        repo.get_generated_svg("test.pcbdoc")


def test_get_generated_json(instance):
    repo = Repository.request(instance, test_org, test_repo)
    branch = repo.get_branches()[0]
    json = retry_not_yet_generated(repo.get_generated_json, "test.pcbdoc", branch)
    assert json is not None
    assert json["type"] == "Pcb"


def test_get_generated_project_json(instance):
    repo = Repository.request(instance, test_org, test_repo)
    branch = repo.get_branches()[0]
    json = retry_not_yet_generated(repo.get_generated_projectdata, "test.pcbdoc", branch)
    assert json is not None


def test_get_generated_svg(instance):
    repo = Repository.request(instance, test_org, test_repo)
    branch = repo.get_branches()[0]
    while True:
        try:
            svg = repo.get_generated_svg("test.pcbdoc", branch)
            break
        except NotYetGeneratedException:
            time.sleep(1)
            pass
    assert svg is not None
    assert svg.startswith(b"<svg")


def test_get_repository_non_existent(instance):
    with pytest.raises(NotFoundException):
        instance.get_repository("doesnotexist", "doesnotexist")


def test_repo_topics(instance):
    # Since topics aren't part of the Repository object directly, we
    # have to test both get and add at the same time.
    repo = Repository.request(instance, test_org, test_repo)
    topics = repo.get_topics()
    assert len(topics) == 0

    repo.add_topic(test_topic)
    topics = repo.get_topics()
    assert len(topics) == 1
    assert topics[0] == test_topic


def test_search_repos(instance):
    repos = Repository.search(instance, test_repo)
    # Two repos have been made with this name so far!
    assert len(repos) == 2
    assert repos[0].name == test_repo

    repos = Repository.search(instance, test_topic, topic=True)
    assert len(repos) == 1
    assert repos[0].name == test_repo


def test_patch_repo(instance):
    fields = {
        "allow_rebase": False,
        "description": "new description",
        "has_projects": True,
        "private": True,
    }
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    for field, value in fields.items():
        setattr(repo, field, value)
    repo.commit()
    repo = org.get_repository(test_repo)
    for field, value in fields.items():
        assert getattr(repo, field) == value


def test_list_branches(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    branches = repo.get_branches()
    assert len(branches) > 0
    master = [b for b in branches if b.name == "master"]
    assert len(master) > 0


def test_get_branch(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    branch = repo.get_branch("master")
    assert branch is not None
    assert branch.name == "master"


def test_get_branch_non_existent(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    with pytest.raises(NotFoundException):
        repo.get_branch("doesnotexist")


def test_list_files_and_content(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    content = repo.get_git_content()
    # Readme file should exist in any new repo
    #  content is the description given during creation
    readmes = [c for c in content if c.name == "README.md"]
    assert len(readmes) > 0
    readme_content = repo.get_file_content(readmes[0])
    assert len(readme_content) > 0
    assert "descr" in str(base64.b64decode(readme_content))


def test_get_raw_file(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    readme_content = repo.get_raw_file("README.md")
    assert len(readme_content) > 0
    assert "descr" in str(readme_content)


def test_repo_download_file(instance, tmp_path):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    filename = uuid.uuid4().hex[:8] + ".md"
    filepath = tmp_path / filename
    with open(filepath, "wb") as f:
        repo.download_to_file("README.md", f)
    with open(filepath, "rb") as f:
        readme_content = f.read().decode("utf-8")
        assert len(readme_content) > 0
        assert "descr" in readme_content


def test_create_file(instance):
    TESTFILE_CONENTE = "TestStringFileContent"
    TESTFILE_CONENTE_B64 = base64.b64encode(bytes(TESTFILE_CONENTE, "utf-8"))
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    repo.create_file("testfile.md", content=TESTFILE_CONENTE_B64.decode("ascii"))
    # test if putting was successful
    content = repo.get_git_content()
    readmes = [c for c in content if c.name == "testfile.md"]
    assert len(readmes) > 0
    readme_content = repo.get_file_content(readmes[0])
    assert len(readme_content) > 0
    assert TESTFILE_CONENTE in str(base64.b64decode(readme_content))


def test_change_file(instance):
    TESTFILE_CONENTE = "TestStringFileContent with changed content now"
    TESTFILE_CONENTE_B64 = base64.b64encode(bytes(TESTFILE_CONENTE, "utf-8"))
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    # figure out the sha of the file to change
    content = repo.get_git_content()
    readmes = [c for c in content if c.name == "testfile.md"]
    # change
    repo.change_file("testfile.md", readmes[0].sha, content=TESTFILE_CONENTE_B64.decode("ascii"))
    # test if putting was successful
    content = repo.get_git_content()
    readmes = [c for c in content if c.name == "testfile.md"]
    assert len(readmes) > 0
    readme_content = repo.get_file_content(readmes[0])
    assert len(readme_content) > 0
    assert TESTFILE_CONENTE in str(base64.b64decode(readme_content))


def test_delete_file(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    # figure out the sha of the file to change
    content = repo.get_git_content()
    readmes = [c for c in content if c.name == "testfile.md"]
    # delete
    repo.delete_file("testfile.md", readmes[0].sha)
    # test if deletion was successful
    content = repo.get_git_content()
    readmes = [c for c in content if c.name == "testfile.md"]
    assert len(readmes) == 0


def test_create_branch(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    branches = repo.get_branches()
    master = [b for b in branches if b.name == "master"]
    assert len(master) > 0
    branch = repo.add_branch(master[0], "test_branch")
    assert branch.name == "test_branch"
    branch = repo.get_branch("test_branch")
    assert branch.name == "test_branch"


def test_create_branch_from_str_ref(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    new_branch_name = "branch-" + uuid.uuid4().hex[:8]
    branch = repo.add_branch("master", new_branch_name)
    assert branch.name == new_branch_name
    branch = repo.get_branch(new_branch_name)
    assert branch.name == new_branch_name


def test_create_team(instance):
    org = Organization.request(instance, test_org)
    team = instance.create_team(org, test_team, "descr")
    assert team.name == test_team
    assert team.description == "descr"
    assert team.organization == org


def test_add_repo_to_team(instance):
    org = Organization.request(instance, test_org)
    team = org.get_team(test_team)
    repository = Repository.request(instance, test_org, test_repo)

    # First with name
    team.add_repo(org, test_repo)
    assert test_repo in [repo.name for repo in team.get_repos()]

    team.delete()

    team = instance.create_team(org, test_team, "descr")
    # Then with object
    team.add_repo(org, repository)
    assert test_repo in [repo.name for repo in team.get_repos()]


def test_create_team_without_units_map(instance):
    org = Organization.request(instance, test_org)
    team = instance.create_team(org, test_team + "1", "descr")
    permission = team.permission
    assert set(team.units_map.keys()) == set(team.units)
    assert list(team.units_map.values()) == [permission] * len(team.units)


def test_create_team_with_units_map(instance):
    org = Organization.request(instance, test_org)
    team = instance.create_team(
        org,
        test_team + "2",
        "descr",
        units_map={"repo.code": "write", "repo.wiki": "admin"},
    )
    assert set(team.units) == set(["repo.code", "repo.wiki"])
    assert team.units_map == {"repo.code": "write", "repo.wiki": "admin"}


def test_patch_team(instance):
    fields = {
        "can_create_org_repo": True,
        "description": "patched description",
        "includes_all_repositories": True,
        "name": "newname",
        "permission": "write",
    }
    org = Organization.request(instance, test_org)
    team = instance.create_team(org, test_team[:1], "descr")
    for field, value in fields.items():
        setattr(team, field, value)
    team.commit()
    team = Team.request(instance, team.id)
    for field, value in fields.items():
        assert getattr(team, field) == value


def test_request_team(instance):
    org = Organization.request(instance, test_org)
    team = org.get_team(test_team)
    team2 = Team.request(instance, team.id)
    assert team.name == team2.name


def test_create_milestone(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repository(test_repo)
    ms = repo.create_milestone("I love this Milestone", "Find an otter to adopt this milestone")
    assert isinstance(ms, Milestone)
    assert ms.title == "I love this Milestone"


def test_user_teams(instance):
    org = Organization.request(instance, test_org)
    team = org.get_team(test_team)
    user = instance.get_user_by_name(test_user)

    team.add_user(user)
    teams = user.get_teams()
    assert team in teams
    team_members = team.get_members()
    assert user in team_members

    team.remove_team_member(user.login)
    teams = user.get_teams()
    assert team not in teams
    team_members = team.get_members()
    assert user not in team_members


def test_get_accessible_repositories(instance):
    user = instance.get_user_by_name(test_user)
    repos = user.get_accessible_repos()
    assert len(repos) > 0


def test_create_issue(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = Issue.create_issue(instance, repo, "TestIssue", "Body text with this issue")
    assert issue.state == Issue.OPENED
    assert issue.title == "TestIssue"
    assert issue.body == "Body text with this issue"


def test_hashing(instance):
    # just call the hash function of each object to see if something bad happens
    org = Organization.request(instance, test_org)
    team = org.get_team(test_team)
    user = instance.get_user_by_name(test_user)
    # TODO test for milestones (Todo: add milestone adding)
    repo = org.get_repositories()[0]
    milestone = repo.create_milestone("mystone", "this is only a teststone")
    issue = repo.get_issues()[0]
    branch = repo.get_branches()[0]
    commit = repo.get_commits()[0]
    assert len(set([org, team, user, repo, issue, branch, commit, milestone]))


def test_change_issue(instance):
    org = Organization.request(instance, test_org)
    repo = org.get_repositories()[0]
    ms_title = "othermilestone"
    issue = Issue.create_issue(instance, repo, "IssueTestissue with Testinput", "asdf2332")
    new_body = "some new description with some more of that char stuff :)"
    issue.body = new_body
    issue.commit()
    number = issue.number
    del issue
    issue2 = Issue.request(instance, org.username, repo.name, number)
    assert issue2.body == new_body
    milestone = repo.create_milestone(ms_title, "this is only a teststone2")
    issue2.milestone = milestone
    issue2.commit()
    del issue2
    issue3 = Issue.request(instance, org.username, repo.name, number)
    assert issue3.milestone is not None
    assert issue3.milestone.description == "this is only a teststone2"
    issues = repo.get_issues()
    assert (
        len(
            [
                issue
                for issue in issues
                if issue.milestone is not None and issue.milestone.title == ms_title
            ]
        )
        > 0
    )


def test_create_issue_attachment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    attachment = issue.create_attachment(open("requirements.txt", "rb"))
    assert attachment.name == "requirements.txt"
    assert attachment.download_count == 0


def test_get_issue_attachments(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    attachments = issue.get_attachments()
    assert len(attachments) > 0
    assert attachments[0].name == "requirements.txt"

    issue = Issue.request(instance, org.username, repo.name, issue.number)
    assert len(issue.assets) == 1
    assert issue.assets[0].name == "requirements.txt"


def test_create_issue_comment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.create_comment("this is a comment")
    assert comment.body == "this is a comment"
    assert comment.user.username == "test"


def test_get_issue_comments(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comments = issue.get_comments()
    assert len(comments) > 0
    assert comments[0].body == "this is a comment"


def test_edit_issue_comment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.get_comments()[0]
    comment.body = "this is a new comment"
    comment.commit()
    assert comment.body == "this is a new comment"
    comment_id = comment.id
    comment2 = Comment.request(instance, org.username, repo.name, comment_id)
    assert comment2.body == "this is a new comment"


def test_delete_issue_comment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.get_comments()[0]
    comment_id = comment.id
    comment.delete()
    with pytest.raises(NotFoundException) as _:
        Comment.request(instance, org.username, repo.name, comment_id)


def test_create_issue_comment_attachment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.create_comment("this is a comment that will have an attachment")
    attachment = comment.create_attachment(open("requirements.txt", "rb"))
    assert attachment.name == "requirements.txt"
    assert attachment.download_count == 0


def test_create_issue_comment_attachment_with_name(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.create_comment("this is a comment that will have an attachment")
    attachment = comment.create_attachment(open("requirements.txt", "rb"), "something else.txt")
    assert attachment.name == "something else.txt"
    assert attachment.download_count == 0


def test_get_issue_comment_attachments(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.get_comments()[0]
    attachments = comment.get_attachments()
    assert len(attachments) > 0
    assert attachments[0].name == "requirements.txt"


def test_download_issue_comment_attachment(instance, tmp_path):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.get_comments()[0]
    attachment = comment.get_attachments()[0]

    filename = uuid.uuid4().hex[:8] + ".txt"
    filepath = tmp_path / filename
    with open(filepath, "wb") as f:
        attachment.download_to_file(f)

    with open(filepath, "r") as actual_f:
        with open("requirements.txt", "r") as expected_f:
            attachment_content = actual_f.read()
            assert len(attachment_content) > 0

            expected_content = expected_f.read()
            assert expected_content == attachment_content


def test_edit_issue_comment_attachment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.get_comments()[0]
    attachment = comment.get_attachments()[0]
    comment.edit_attachment(attachment, {"name": "this is a new attachment.txt"})
    del attachment
    attachment2 = comment.get_attachments()[0]
    assert attachment2.name == "this is a new attachment.txt"


def test_delete_issue_comment_attachment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    issue = repo.get_issues()[0]
    comment = issue.get_comments()[0]
    attachment = comment.get_attachments()[0]
    comment.delete_attachment(attachment)
    assert len(comment.get_attachments()) == 0


def test_create_design_review(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    branch = Branch.request(instance, org.username, test_repo, "master")
    repo.create_file(
        "new_file.txt",
        base64.b64encode(b"new file contents").decode("utf-8"),
        {"branch": "test_branch"},
    )
    due_date = datetime.datetime.now() + datetime.timedelta(days=7)
    review = repo.create_design_review(
        "TestDesignReview",
        "test_branch",
        branch,
        body="This is a test review",
        assignees=["test"],
        due_date=due_date,
    )

    assert review.state == DesignReview.OPEN
    assert review.title == "TestDesignReview"
    assert review.base == "master"
    assert review.head == "test_branch"
    assert review.body == "This is a test review"
    assert review.assignees[0].username == "test"

    review_due_date = Util.convert_time(review.due_date)
    assert review_due_date.date() == due_date.date()


def test_get_design_reviews(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]

    assert dr.title == "TestDesignReview"
    assert dr.base == "master"
    assert dr.head == "test_branch"
    assert dr.body == "This is a test review"


def test_edit_design_review(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    new_branch = repo.add_branch(repo.get_branch("master"), "test_branch2")
    dr.title = "TestDesignReview2"
    dr.body = "This is a test review2"
    dr.due_date = None
    dr.base = new_branch
    dr.commit()
    del dr
    dr = repo.get_design_reviews()[0]
    assert dr.title == "TestDesignReview2"
    assert dr.base == "test_branch2"
    assert dr.head == "test_branch"
    assert dr.body == "This is a test review2"
    assert dr.due_date is None


def test_create_design_review_comment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    comment = dr.create_comment("This is a test comment")
    assert comment.body == "This is a test comment"


def test_get_design_review_comments(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    comments = dr.get_comments()
    assert len(comments) > 0
    assert comments[0].body == "This is a test comment"


def test_add_design_review_comment_attachment(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    comment = dr.get_comments()[0]
    attachment = comment.create_attachment(open("requirements.txt", "rb"))
    assert attachment.name == "requirements.txt"
    assert attachment.download_count == 0


def test_get_design_review_attachments(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    comment = dr.get_comments()[0]
    attachments = comment.get_attachments()
    assert len(attachments) > 0
    assert attachments[0].name == "requirements.txt"


def test_create_design_review_review(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    review = dr.create_review(
        body="New Review",
        comments=[DesignReviewReview.ReviewComment("Comment within review", "new_file.txt")],
    )

    assert review.body == "New Review"
    assert review.comments_count == 1
    assert review.state == DesignReviewReview.ReviewEvent.PENDING


def test_get_design_review_reviews(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    reviews = dr.get_reviews()
    assert len(reviews) > 0
    assert reviews[0].body == "New Review"


def test_get_design_review_review_comments(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    review = dr.get_reviews()[0]
    comments = review.get_comments()

    assert len(comments) == 1
    assert comments[0].body == "Comment within review"


def test_submit_design_review_review(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    review = dr.get_reviews()[0]
    assert review.state == DesignReviewReview.ReviewEvent.PENDING
    dr.submit_review(review.id, DesignReviewReview.ReviewEvent.COMMENT, body="New Body")
    del review
    review = dr.get_reviews()[0]
    assert review.state == DesignReviewReview.ReviewEvent.COMMENT
    assert review.body == "New Body"


def test_drr_computed_properties(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    review = dr.get_reviews()[0]

    assert review.owner_name == org.username
    assert review.repository_name == repo.name
    assert int(review.index) == dr.number


def test_drr_computed_properties_on_server_with_subpath(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    review = dr.get_reviews()[0]
    # Hacky, but works for a test without having to set up a real server with a
    # subpath. Note that "owner" and "repo" are not the actual names (which are
    # randomly generated and guaranteed to not be these strings) of the owner
    # and repo, so this ensures the computed properties work.
    review.__setattr__("_pull_request_url", "https://hub.allspice.io/subpath/owner/repo/pulls/1")

    assert review.owner_name == "owner"
    assert review.repository_name == "repo"
    assert review.index == "1"


def test_delete_design_review_review(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]
    review = dr.get_reviews()[0]
    review.delete()

    reviews = dr.get_reviews()
    assert len(reviews) == 0


def test_merge_design_review(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    dr = repo.get_design_reviews()[0]

    assert dr.state == "open"

    # The API may fail with this message. It isn't in the scope of this test to
    # make sure the API can merge, so we'll keep retrying until it works or we
    # retry too many times.
    attempts = 0
    while attempts < 5:
        try:
            dr.merge(DesignReview.MergeType.MERGE)
            break
        except Exception as e:
            if "Please try again later" in str(e):
                attempts += 1
                time.sleep(1)
                continue
            else:
                raise e

    dr = repo.get_design_reviews()[0]
    assert dr.state == "closed"


def test_repo_create_release(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    # Just a tag should be enough.
    release = repo.create_release("v0.0.1")
    assert release.tag_name == "v0.0.1"
    release = repo.create_release("v0.1.0", "v0.1.0 release", "release with new tag")
    assert release.tag_name == "v0.1.0"
    assert release.name == "v0.1.0 release"
    assert release.body == "release with new tag"


def test_get_repo_releases(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    releases = repo.get_releases()
    assert len(releases) > 0
    assert releases[0].name == "v0.1.0 release"


def test_get_repo_latest_release(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    assert release is not None
    assert release.name == "v0.1.0 release"


def test_get_release_by_tag(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_release_by_tag("v0.1.0")
    assert release is not None
    assert release.name == "v0.1.0 release"


def test_edit_release(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    # Note that the tag hasn't changed
    release.name = "v0.1.1 release"
    release.body = "release with changed name"
    release.commit()
    del release
    release = repo.get_latest_release()
    assert release.name == "v0.1.1 release"
    assert release.body == "release with changed name"


def test_create_release_asset(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    asset = release.create_asset(open("requirements.txt", "rb"))
    assert asset.name == "requirements.txt"
    assert asset.download_count == 0


def test_create_release_asset_with_name(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    asset = release.create_asset(open("requirements.txt", "rb"), "something else.txt")
    assert asset.name == "something else.txt"
    assert asset.download_count == 0


def test_get_release_assets(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    assert len(release.assets) > 0
    assert release.assets[0].name == "requirements.txt"


def test_download_release_asset(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    asset = release.assets[0]
    data = asset.download()
    assert data == open("requirements.txt", "rb").read()


def test_delete_release_asset(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    asset = release.assets[0]
    asset.delete()
    assert len(release.assets) == (len(repo.get_latest_release().assets) + 1)


def test_delete_release(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    release = repo.get_latest_release()
    old_releases = repo.get_releases()
    release.delete()
    assert len(repo.get_releases()) == len(old_releases) - 1


def test_create_commit_status(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    commit = repo.get_commits()[0]
    status = repo.create_commit_status(
        commit,
        state=CommitStatusState.ERROR,
        context="This is a test status",
    )
    assert status.status == CommitStatusState.ERROR
    assert status.context == "This is a test status"
    assert status.description == ""


def test_get_commit_statuses(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    commit = repo.get_commits()[0]
    statuses = commit.get_statuses()
    assert len(statuses) > 0
    assert statuses[0].context == "This is a test status"


def test_get_commit_combined_status(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    commit = repo.get_commits()[0]
    status = commit.get_status()
    assert status is not None
    assert status.state == CommitStatusState.FAILURE


def test_get_commit_status_from(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    commit = repo.get_commits()[0]
    statuses = repo.get_commit_statuses(commit, state=CommitStatusState.SUCCESS)
    assert len(statuses) == 0
    statuses = repo.get_commit_statuses(commit, state=CommitStatusState.ERROR)
    assert len(statuses) == 1


def test_get_repo_archive(instance):
    # This requires a repo with actual files in it, so we use the test repo
    repo = Repository.request(instance, test_org, test_repo)
    branch = repo.get_branches()[0]
    archive = repo.get_archive(branch)
    assert archive is not None


def test_team_get_org(instance):
    org = Organization.request(instance, test_org)
    team = org.get_team(test_team)
    assert org.username == team.organization.name


def test_delete_repo_userowned(instance):
    user = User.request(instance, test_user)
    repo = Repository.request(instance, user.username, test_repo)
    repo.delete()
    with pytest.raises(NotFoundException):
        Repository.request(instance, test_user, test_repo)


def test_secondary_email(instance):
    SECONDARYMAIL = "secondarytest@test.org"  # set up with real email
    sec_user = instance.get_user_by_email(SECONDARYMAIL)
    assert SECONDARYMAIL in sec_user.emails
    assert sec_user.username == "test"


def test_delete_repo_orgowned(instance):
    org = Organization.request(instance, test_org)
    repo = Repository.request(instance, org.username, test_repo)
    repo.delete()
    with pytest.raises(NotFoundException):
        Repository.request(instance, test_user, test_repo)


def test_change_repo_ownership_org(instance):
    old_org = Organization.request(instance, test_org)
    user = User.request(instance, test_user)
    new_org = instance.create_org(
        user, test_org + "_repomove", "Org for testing moving repositories"
    )
    new_team = instance.create_team(new_org, test_team + "_repomove", "descr")
    repo_name = test_repo + "_repomove"
    repo = instance.create_repo(old_org, repo_name, "descr")
    repo.transfer_ownership(new_org, set([new_team]))
    assert repo_name not in [repo.name for repo in old_org.get_repositories()]
    assert repo_name in [repo.name for repo in new_org.get_repositories()]


def test_change_repo_ownership_user(instance):
    old_org = Organization.request(instance, test_org)
    user = User.request(instance, test_user)
    repo_name = test_repo + "_repomove"
    repo = instance.create_repo(old_org, repo_name, "descr")
    repo.transfer_ownership(user)
    assert repo_name not in [repo.name for repo in old_org.get_repositories()]
    assert repo_name in [repo.name for repo in user.get_repositories()]
    for repo in user.get_repositories():
        repo.transfer_ownership(old_org)
        assert repo_name in [repo.name for repo in old_org.get_repositories()]
        assert repo_name not in [repo.name for repo in user.get_repositories()]


def test_delete_team(instance):
    org = Organization.request(instance, test_org)
    team = org.get_team(test_team)
    team.delete()
    with pytest.raises(NotFoundException):
        team = org.get_team(test_team)


def test_delete_teams(instance):
    org = Organization.request(instance, test_org)
    repos = org.get_repositories()
    for repo in repos:
        repo.delete()
    repos = org.get_repositories()
    assert len(repos) == 0


def test_delete_org(instance):
    org = Organization.request(instance, test_org)
    org.delete()
    with pytest.raises(NotFoundException):
        Organization.request(instance, test_org)


def test_delete_user(instance):
    user_name = test_user + "delte_test"
    email = user_name + "@example.org"
    user = instance.create_user(user_name, email, "abcdefg1.23AB", send_notify=False)
    assert user.username == user_name
    user.delete()
    with pytest.raises(NotFoundException):
        User.request(instance, user_name)
