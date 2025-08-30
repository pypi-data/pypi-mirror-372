# cSpell:words ECAD

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from functools import cached_property
from typing import (
    IO,
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

try:
    from typing_extensions import Self
except ImportError:
    from typing import Self

from .baseapiobject import ApiObject, ReadonlyApiObject
from .exceptions import ConflictException, NotFoundException


class Organization(ApiObject):
    """see https://hub.allspice.io/api/swagger#/organization/orgGetAll"""

    active: Optional[bool]
    avatar_url: str
    created: Optional[str]
    description: str
    email: str
    followers_count: Optional[int]
    following_count: Optional[int]
    full_name: str
    html_url: Optional[str]
    id: int
    is_admin: Optional[bool]
    language: Optional[str]
    last_login: Optional[str]
    location: str
    login: Optional[str]
    login_name: Optional[str]
    name: Optional[str]
    prohibit_login: Optional[bool]
    repo_admin_change_team_access: Optional[bool]
    restricted: Optional[bool]
    source_id: Optional[int]
    starred_repos_count: Optional[int]
    username: str
    visibility: str
    website: str

    API_OBJECT = """/orgs/{name}"""  # <org>
    ORG_REPOS_REQUEST = """/orgs/%s/repos"""  # <org>
    ORG_TEAMS_REQUEST = """/orgs/%s/teams"""  # <org>
    ORG_TEAMS_CREATE = """/orgs/%s/teams"""  # <org>
    ORG_GET_MEMBERS = """/orgs/%s/members"""  # <org>
    ORG_IS_MEMBER = """/orgs/%s/members/%s"""  # <org>, <username>
    ORG_HEATMAP = """/users/%s/heatmap"""  # <username>

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Organization):
            return False
        return self.allspice_client == other.allspice_client and self.name == other.name

    def __hash__(self):
        return hash(self.allspice_client) ^ hash(self.name)

    @classmethod
    def request(cls, allspice_client, name: str) -> Self:
        return cls._request(allspice_client, {"name": name})

    @classmethod
    def parse_response(cls, allspice_client, result) -> "Organization":
        api_object = super().parse_response(allspice_client, result)
        # add "name" field to make this behave similar to users for gitea < 1.18
        # also necessary for repository-owner when org is repo owner
        if not hasattr(api_object, "name"):
            Organization._add_read_property("name", result["username"], api_object)
        return api_object

    _patchable_fields: ClassVar[set[str]] = {
        "description",
        "full_name",
        "location",
        "visibility",
        "website",
    }

    def commit(self):
        args = {"name": self.name}
        self._commit(args)

    def create_repo(
        self,
        repoName: str,
        description: str = "",
        private: bool = False,
        autoInit=True,
        gitignores: Optional[str] = None,
        license: Optional[str] = None,
        readme: str = "Default",
        issue_labels: Optional[str] = None,
        default_branch="master",
    ):
        """Create an organization Repository

        Throws:
            AlreadyExistsException: If the Repository exists already.
            Exception: If something else went wrong.
        """
        result = self.allspice_client.requests_post(
            f"/orgs/{self.name}/repos",
            data={
                "name": repoName,
                "description": description,
                "private": private,
                "auto_init": autoInit,
                "gitignores": gitignores,
                "license": license,
                "issue_labels": issue_labels,
                "readme": readme,
                "default_branch": default_branch,
            },
        )
        if "id" in result:
            self.allspice_client.logger.info("Successfully created Repository %s " % result["name"])
        else:
            self.allspice_client.logger.error(result["message"])
            raise Exception("Repository not created... (gitea: %s)" % result["message"])
        return Repository.parse_response(self.allspice_client, result)

    def get_repositories(self) -> List["Repository"]:
        results = self.allspice_client.requests_get_paginated(
            Organization.ORG_REPOS_REQUEST % self.username
        )
        return [Repository.parse_response(self.allspice_client, result) for result in results]

    def get_repository(self, name) -> "Repository":
        repos = self.get_repositories()
        for repo in repos:
            if repo.name == name:
                return repo
        raise NotFoundException("Repository %s not existent in organization." % name)

    def get_teams(self) -> List["Team"]:
        results = self.allspice_client.requests_get(Organization.ORG_TEAMS_REQUEST % self.username)
        teams = [Team.parse_response(self.allspice_client, result) for result in results]
        # organisation seems to be missing using this request, so we add org manually
        for t in teams:
            setattr(t, "_organization", self)
        return teams

    def get_team(self, name) -> "Team":
        teams = self.get_teams()
        for team in teams:
            if team.name == name:
                return team
        raise NotFoundException("Team not existent in organization.")

    def create_team(
        self,
        name: str,
        description: str = "",
        permission: str = "read",
        can_create_org_repo: bool = False,
        includes_all_repositories: bool = False,
        units=(
            "repo.code",
            "repo.issues",
            "repo.ext_issues",
            "repo.wiki",
            "repo.pulls",
            "repo.releases",
            "repo.ext_wiki",
        ),
        units_map={},
    ) -> "Team":
        """Alias for AllSpice#create_team"""
        # TODO: Move AllSpice#create_team to Organization#create_team and
        #       deprecate AllSpice#create_team.
        return self.allspice_client.create_team(
            org=self,
            name=name,
            description=description,
            permission=permission,
            can_create_org_repo=can_create_org_repo,
            includes_all_repositories=includes_all_repositories,
            units=units,
            units_map=units_map,
        )

    def get_members(self) -> List["User"]:
        results = self.allspice_client.requests_get(Organization.ORG_GET_MEMBERS % self.username)
        return [User.parse_response(self.allspice_client, result) for result in results]

    def is_member(self, username) -> bool:
        if isinstance(username, User):
            username = username.username
        try:
            # returns 204 if its ok, 404 if its not
            self.allspice_client.requests_get(
                Organization.ORG_IS_MEMBER % (self.username, username)
            )
            return True
        except Exception:
            return False

    def remove_member(self, user: "User"):
        path = f"/orgs/{self.username}/members/{user.username}"
        self.allspice_client.requests_delete(path)

    def delete(self):
        """Delete this Organization. Invalidates this Objects data. Also deletes all Repositories owned by the User"""
        for repo in self.get_repositories():
            repo.delete()
        self.allspice_client.requests_delete(Organization.API_OBJECT.format(name=self.username))
        self.deleted = True

    def get_heatmap(self) -> List[Tuple[datetime, int]]:
        results = self.allspice_client.requests_get(User.USER_HEATMAP % self.username)
        results = [
            (datetime.fromtimestamp(result["timestamp"]), result["contributions"])
            for result in results
        ]
        return results


class User(ApiObject):
    active: bool
    admin: Any
    allow_create_organization: Any
    allow_git_hook: Any
    allow_import_local: Any
    avatar_url: str
    created: str
    description: str
    email: str
    emails: List[Any]
    followers_count: int
    following_count: int
    full_name: str
    html_url: str
    id: int
    is_admin: bool
    language: str
    last_login: str
    location: str
    login: str
    login_name: str
    max_repo_creation: Any
    must_change_password: Any
    password: Any
    prohibit_login: bool
    restricted: bool
    source_id: int
    starred_repos_count: int
    username: str
    visibility: str
    website: str

    API_OBJECT = """/users/{name}"""  # <org>
    USER_MAIL = """/user/emails?sudo=%s"""  # <name>
    USER_PATCH = """/admin/users/%s"""  # <username>
    ADMIN_DELETE_USER = """/admin/users/%s"""  # <username>
    ADMIN_EDIT_USER = """/admin/users/{username}"""  # <username>
    USER_HEATMAP = """/users/%s/heatmap"""  # <username>

    def __init__(self, allspice_client):
        super().__init__(allspice_client)
        self._emails = []

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.allspice_client == other.allspice_client and self.id == other.id

    def __hash__(self):
        return hash(self.allspice_client) ^ hash(self.id)

    @property
    def emails(self):
        self.__request_emails()
        return self._emails

    @classmethod
    def request(cls, allspice_client, name: str) -> "User":
        api_object = cls._request(allspice_client, {"name": name})
        return api_object

    _patchable_fields: ClassVar[set[str]] = {
        "active",
        "admin",
        "allow_create_organization",
        "allow_git_hook",
        "allow_import_local",
        "email",
        "full_name",
        "location",
        "login_name",
        "max_repo_creation",
        "must_change_password",
        "password",
        "prohibit_login",
        "website",
    }

    def commit(self, login_name: str, source_id: int = 0):
        """
        Unfortunately it is necessary to require the login name
        as well as the login source (that is not supplied when getting a user) for
        changing a user.
        Usually source_id is 0 and the login_name is equal to the username.
        """
        values = self.get_dirty_fields()
        values.update(
            # api-doc says that the "source_id" is necessary; works without though
            {"login_name": login_name, "source_id": source_id}
        )
        args = {"username": self.username}
        self.allspice_client.requests_patch(User.ADMIN_EDIT_USER.format(**args), data=values)
        self._dirty_fields = {}

    def create_repo(
        self,
        repoName: str,
        description: str = "",
        private: bool = False,
        autoInit=True,
        gitignores: Optional[str] = None,
        license: Optional[str] = None,
        readme: str = "Default",
        issue_labels: Optional[str] = None,
        default_branch="master",
    ):
        """Create a user Repository

        Throws:
            AlreadyExistsException: If the Repository exists already.
            Exception: If something else went wrong.
        """
        result = self.allspice_client.requests_post(
            "/user/repos",
            data={
                "name": repoName,
                "description": description,
                "private": private,
                "auto_init": autoInit,
                "gitignores": gitignores,
                "license": license,
                "issue_labels": issue_labels,
                "readme": readme,
                "default_branch": default_branch,
            },
        )
        if "id" in result:
            self.allspice_client.logger.info("Successfully created Repository %s " % result["name"])
        else:
            self.allspice_client.logger.error(result["message"])
            raise Exception("Repository not created... (gitea: %s)" % result["message"])
        return Repository.parse_response(self.allspice_client, result)

    def get_repositories(self) -> List["Repository"]:
        """Get all Repositories owned by this User."""
        url = f"/users/{self.username}/repos"
        results = self.allspice_client.requests_get_paginated(url)
        return [Repository.parse_response(self.allspice_client, result) for result in results]

    def get_orgs(self) -> List[Organization]:
        """Get all Organizations this user is a member of."""
        url = f"/users/{self.username}/orgs"
        results = self.allspice_client.requests_get_paginated(url)
        return [Organization.parse_response(self.allspice_client, result) for result in results]

    def get_teams(self) -> List["Team"]:
        url = "/user/teams"
        results = self.allspice_client.requests_get_paginated(url, sudo=self)
        return [Team.parse_response(self.allspice_client, result) for result in results]

    def get_accessible_repos(self) -> List["Repository"]:
        """Get all Repositories accessible by the logged in User."""
        results = self.allspice_client.requests_get("/user/repos", sudo=self)
        return [Repository.parse_response(self.allspice_client, result) for result in results]

    def __request_emails(self):
        result = self.allspice_client.requests_get(User.USER_MAIL % self.login)
        # report if the adress changed by this
        for mail in result:
            self._emails.append(mail["email"])
            if mail["primary"]:
                self._email = mail["email"]

    def delete(self):
        """Deletes this User. Also deletes all Repositories he owns."""
        self.allspice_client.requests_delete(User.ADMIN_DELETE_USER % self.username)
        self.deleted = True

    def get_heatmap(self) -> List[Tuple[datetime, int]]:
        results = self.allspice_client.requests_get(User.USER_HEATMAP % self.username)
        results = [
            (datetime.fromtimestamp(result["timestamp"]), result["contributions"])
            for result in results
        ]
        return results


class Branch(ReadonlyApiObject):
    commit: Dict[str, Optional[Union[str, Dict[str, str], Dict[str, Optional[Union[bool, str]]]]]]
    effective_branch_protection_name: str
    enable_status_check: bool
    name: str
    protected: bool
    required_approvals: int
    status_check_contexts: List[Any]
    user_can_merge: bool
    user_can_push: bool

    API_OBJECT = """/repos/{owner}/{repo}/branches/{branch}"""

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Branch):
            return False
        return self.commit == other.commit and self.name == other.name

    def __hash__(self):
        return hash(self.commit["id"]) ^ hash(self.name)

    _fields_to_parsers: ClassVar[dict] = {
        # This is not a commit object
        # "commit": lambda allspice_client, c: Commit.parse_response(allspice_client, c)
    }

    @classmethod
    def request(cls, allspice_client, owner: str, repo: str, branch: str):
        return cls._request(allspice_client, {"owner": owner, "repo": repo, "branch": branch})


class GitEntry(ReadonlyApiObject):
    """
    An object representing a file or directory in the Git tree.
    """

    mode: str
    path: str
    sha: str
    size: int
    type: str
    url: str

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other) -> bool:
        if not isinstance(other, GitEntry):
            return False
        return self.sha == other.sha

    def __hash__(self) -> int:
        return hash(self.sha)


class Repository(ApiObject):
    allow_fast_forward_only_merge: bool
    allow_manual_merge: Any
    allow_merge_commits: bool
    allow_rebase: bool
    allow_rebase_explicit: bool
    allow_rebase_update: bool
    allow_squash_merge: bool
    archived: bool
    archived_at: str
    autodetect_manual_merge: Any
    avatar_url: str
    clone_url: str
    created_at: str
    default_allow_maintainer_edit: bool
    default_branch: str
    default_delete_branch_after_merge: bool
    default_merge_style: str
    description: str
    empty: bool
    enable_prune: Any
    external_tracker: Any
    external_wiki: Any
    fork: bool
    forks_count: int
    full_name: str
    has_actions: bool
    has_issues: bool
    has_packages: bool
    has_projects: bool
    has_pull_requests: bool
    has_releases: bool
    has_wiki: bool
    html_url: str
    id: int
    ignore_whitespace_conflicts: bool
    internal: bool
    internal_tracker: Dict[str, bool]
    language: str
    languages_url: str
    licenses: Any
    link: str
    mirror: bool
    mirror_interval: str
    mirror_updated: str
    name: str
    object_format_name: str
    open_issues_count: int
    open_pr_counter: int
    original_url: str
    owner: Union["User", "Organization"]
    parent: Any
    permissions: Dict[str, bool]
    private: bool
    projects_mode: str
    release_counter: int
    repo_transfer: Any
    size: int
    ssh_url: str
    stars_count: int
    template: bool
    topics: List[Union[Any, str]]
    updated_at: datetime
    url: str
    watchers_count: int
    website: str

    API_OBJECT = """/repos/{owner}/{name}"""  # <owner>, <reponame>
    REPO_IS_COLLABORATOR = """/repos/%s/%s/collaborators/%s"""  # <owner>, <reponame>, <username>
    REPO_SEARCH = """/repos/search/"""
    REPO_BRANCHES = """/repos/%s/%s/branches"""  # <owner>, <reponame>
    REPO_BRANCH = """/repos/{owner}/{repo}/branches/{branch}"""
    REPO_ISSUES = """/repos/{owner}/{repo}/issues"""  # <owner, reponame>
    REPO_DESIGN_REVIEWS = """/repos/{owner}/{repo}/pulls"""
    REPO_DELETE = """/repos/%s/%s"""  # <owner>, <reponame>
    REPO_TIMES = """/repos/%s/%s/times"""  # <owner>, <reponame>
    REPO_USER_TIME = """/repos/%s/%s/times/%s"""  # <owner>, <reponame>, <username>
    REPO_COMMITS = "/repos/%s/%s/commits"  # <owner>, <reponame>
    REPO_TRANSFER = "/repos/{owner}/{repo}/transfer"
    REPO_MILESTONES = """/repos/{owner}/{repo}/milestones"""
    REPO_GET_ARCHIVE = "/repos/{owner}/{repo}/archive/{ref}.{format}"
    REPO_GET_ALLSPICE_JSON = "/repos/{owner}/{repo}/allspice_generated/json/{content}"
    REPO_GET_ALLSPICE_SVG = "/repos/{owner}/{repo}/allspice_generated/svg/{content}"
    REPO_GET_ALLSPICE_PROJECT = "/repos/{owner}/{repo}/allspice_generated/project/{content}"
    REPO_GET_TOPICS = "/repos/{owner}/{repo}/topics"
    REPO_ADD_TOPIC = "/repos/{owner}/{repo}/topics/{topic}"
    REPO_GET_RELEASES = "/repos/{owner}/{repo}/releases"
    REPO_GET_LATEST_RELEASE = "/repos/{owner}/{repo}/releases/latest"
    REPO_GET_RELEASE_BY_TAG = "/repos/{owner}/{repo}/releases/tags/{tag}"
    REPO_GET_COMMIT_STATUS = "/repos/{owner}/{repo}/statuses/{sha}"
    REPO_GET_RAW_FILE = "/repos/{owner}/{repo}/raw/{path}"
    REPO_GET_TREE = "/repos/{owner}/{repo}/git/trees/{ref}"

    class ArchiveFormat(Enum):
        """
        Archive formats for Repository.get_archive
        """

        TAR = "tar.gz"
        ZIP = "zip"

    class CommitStatusSort(Enum):
        """
        Sort order for Repository.get_commit_status
        """

        OLDEST = "oldest"
        RECENT_UPDATE = "recentupdate"
        LEAST_UPDATE = "leastupdate"
        LEAST_INDEX = "leastindex"
        HIGHEST_INDEX = "highestindex"

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Repository):
            return False
        return self.owner == other.owner and self.name == other.name

    def __hash__(self):
        return hash(self.owner) ^ hash(self.name)

    _fields_to_parsers: ClassVar[dict] = {
        # dont know how to tell apart user and org as owner except form email being empty.
        "owner": lambda allspice_client, r: (
            Organization.parse_response(allspice_client, r)
            if r["email"] == ""
            else User.parse_response(allspice_client, r)
        ),
        "updated_at": lambda _, t: Util.convert_time(t),
    }

    @classmethod
    def request(
        cls,
        allspice_client,
        owner: str,
        name: str,
    ) -> Repository:
        return cls._request(allspice_client, {"owner": owner, "name": name})

    @classmethod
    def search(
        cls,
        allspice_client,
        query: Optional[str] = None,
        topic: bool = False,
        include_description: bool = False,
        user: Optional[User] = None,
        owner_to_prioritize: Union[User, Organization, None] = None,
    ) -> list[Repository]:
        """
        Search for repositories.

        See https://hub.allspice.io/api/swagger#/repository/repoSearch

        :param query: The query string to search for
        :param topic: If true, the query string will only be matched against the
            repository's topic.
        :param include_description: If true, the query string will be matched
            against the repository's description as well.
        :param user: If specified, only repositories that this user owns or
            contributes to will be searched.
        :param owner_to_prioritize: If specified, repositories owned by the
            given entity will be prioritized in the search.
        :returns: All repositories matching the query. If there are many
            repositories matching this query, this may take some time.
        """

        params = {}

        if query is not None:
            params["q"] = query
        if topic:
            params["topic"] = topic
        if include_description:
            params["include_description"] = include_description
        if user is not None:
            params["user"] = user.id
        if owner_to_prioritize is not None:
            params["owner_to_prioritize"] = owner_to_prioritize.id

        responses = allspice_client.requests_get_paginated(cls.REPO_SEARCH, params=params)

        return [Repository.parse_response(allspice_client, response) for response in responses]

    _patchable_fields: ClassVar[set[str]] = {
        "allow_manual_merge",
        "allow_merge_commits",
        "allow_rebase",
        "allow_rebase_explicit",
        "allow_rebase_update",
        "allow_squash_merge",
        "archived",
        "autodetect_manual_merge",
        "default_branch",
        "default_delete_branch_after_merge",
        "default_merge_style",
        "description",
        "enable_prune",
        "external_tracker",
        "external_wiki",
        "has_actions",
        "has_issues",
        "has_projects",
        "has_pull_requests",
        "has_wiki",
        "ignore_whitespace_conflicts",
        "internal_tracker",
        "mirror_interval",
        "name",
        "private",
        "template",
        "website",
    }

    def commit(self):
        args = {"owner": self.owner.username, "name": self.name}
        self._commit(args)

    def get_branches(self) -> List["Branch"]:
        """Get all the Branches of this Repository."""

        results = self.allspice_client.requests_get_paginated(
            Repository.REPO_BRANCHES % (self.owner.username, self.name)
        )
        return [Branch.parse_response(self.allspice_client, result) for result in results]

    def get_branch(self, name: str) -> "Branch":
        """Get a specific Branch of this Repository."""
        result = self.allspice_client.requests_get(
            Repository.REPO_BRANCH.format(owner=self.owner.username, repo=self.name, branch=name)
        )
        return Branch.parse_response(self.allspice_client, result)

    def add_branch(self, create_from: Ref, newname: str) -> "Branch":
        """Add a branch to the repository"""
        # Note: will only work with gitea 1.13 or higher!

        ref_name = Util.data_params_for_ref(create_from)
        if "ref" not in ref_name:
            raise ValueError("create_from must be a Branch, Commit or string")
        ref_name = ref_name["ref"]

        data = {"new_branch_name": newname, "old_ref_name": ref_name}
        result = self.allspice_client.requests_post(
            Repository.REPO_BRANCHES % (self.owner.username, self.name), data=data
        )
        return Branch.parse_response(self.allspice_client, result)

    def get_issues(
        self,
        state: Literal["open", "closed", "all"] = "all",
        search_query: Optional[str] = None,
        labels: Optional[List[str]] = None,
        milestones: Optional[List[Union[Milestone, str]]] = None,
        assignee: Optional[Union[User, str]] = None,
        since: Optional[datetime] = None,
        before: Optional[datetime] = None,
    ) -> List["Issue"]:
        """
        Get all Issues of this Repository (open and closed)

        https://hub.allspice.io/api/swagger#/repository/repoListIssues

        All params of this method are optional filters. If you don't specify a filter, it
        will not be applied.

        :param state: The state of the Issues to get. If None, all Issues are returned.
        :param search_query: Filter issues by text. This is equivalent to searching for
                             `search_query` in the Issues on the web interface.
        :param labels: Filter issues by labels.
        :param milestones: Filter issues by milestones.
        :param assignee: Filter issues by the assigned user.
        :param since: Filter issues by the date they were created.
        :param before: Filter issues by the date they were created.
        :return: A list of Issues.
        """

        data = {
            "state": state,
        }
        if search_query:
            data["q"] = search_query
        if labels:
            data["labels"] = ",".join(labels)
        if milestones:
            data["milestone"] = ",".join(
                [
                    milestone.name if isinstance(milestone, Milestone) else milestone
                    for milestone in milestones
                ]
            )
        if assignee:
            if isinstance(assignee, User):
                data["assignee"] = assignee.username
            else:
                data["assignee"] = assignee
        if since:
            data["since"] = Util.format_time(since)
        if before:
            data["before"] = Util.format_time(before)

        results = self.allspice_client.requests_get_paginated(
            Repository.REPO_ISSUES.format(owner=self.owner.username, repo=self.name),
            params=data,
        )

        issues = []
        for result in results:
            issue = Issue.parse_response(self.allspice_client, result)
            # See Issue.request
            setattr(issue, "_repository", self)
            # This is mostly for compatibility with an older implementation
            Issue._add_read_property("repo", self, issue)
            issues.append(issue)

        return issues

    def get_design_reviews(
        self,
        state: Literal["open", "closed", "all"] = "all",
        milestone: Optional[Union[Milestone, str]] = None,
        labels: Optional[List[str]] = None,
    ) -> List["DesignReview"]:
        """
        Get all Design Reviews of this Repository.

        https://hub.allspice.io/api/swagger#/repository/repoListPullRequests

        :param state: The state of the Design Reviews to get. If None, all Design Reviews
                      are returned.
        :param milestone: The milestone of the Design Reviews to get.
        :param labels: A list of label IDs to filter DRs by.
        :return: A list of Design Reviews.
        """

        params = {
            "state": state,
        }
        if milestone:
            if isinstance(milestone, Milestone):
                params["milestone"] = milestone.name
            else:
                params["milestone"] = milestone
        if labels:
            params["labels"] = ",".join(labels)

        results = self.allspice_client.requests_get_paginated(
            self.REPO_DESIGN_REVIEWS.format(owner=self.owner.username, repo=self.name),
            params=params,
        )
        return [DesignReview.parse_response(self.allspice_client, result) for result in results]

    def get_commits(
        self,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        stat: bool = True,
    ) -> List["Commit"]:
        """
        Get all the Commits of this Repository.

        https://hub.allspice.io/api/swagger#/repository/repoGetAllCommits

        :param sha: The SHA of the commit to start listing commits from.
        :param path: filepath of a file/dir.
        :param stat: Include the number of additions and deletions in the response.
                     Disable for speedup.
        :return: A list of Commits.
        """

        data = {}
        if sha:
            data["sha"] = sha
        if path:
            data["path"] = path
        if not stat:
            data["stat"] = False

        try:
            results = self.allspice_client.requests_get_paginated(
                Repository.REPO_COMMITS % (self.owner.username, self.name),
                params=data,
            )
        except ConflictException as err:
            logging.warning(err)
            logging.warning("Repository %s/%s is Empty" % (self.owner.username, self.name))
            results = []
        return [Commit.parse_response(self.allspice_client, result) for result in results]

    def get_issues_state(self, state) -> List["Issue"]:
        """
        DEPRECATED: Use get_issues() instead.

        Get issues of state Issue.open or Issue.closed of a repository.
        """

        assert state in [Issue.OPENED, Issue.CLOSED]
        issues = []
        data = {"state": state}
        results = self.allspice_client.requests_get_paginated(
            Repository.REPO_ISSUES.format(owner=self.owner.username, repo=self.name),
            params=data,
        )
        for result in results:
            issue = Issue.parse_response(self.allspice_client, result)
            # adding data not contained in the issue response
            # See Issue.request()
            setattr(issue, "_repository", self)
            Issue._add_read_property("repo", self, issue)
            Issue._add_read_property("owner", self.owner, issue)
            issues.append(issue)
        return issues

    def get_times(self):
        results = self.allspice_client.requests_get(
            Repository.REPO_TIMES % (self.owner.username, self.name)
        )
        return results

    def get_user_time(self, username) -> float:
        if isinstance(username, User):
            username = username.username
        results = self.allspice_client.requests_get(
            Repository.REPO_USER_TIME % (self.owner.username, self.name, username)
        )
        time = sum(r["time"] for r in results)
        return time

    def get_full_name(self) -> str:
        return self.owner.username + "/" + self.name

    def create_issue(self, title, assignees=frozenset(), description="") -> ApiObject:
        data = {
            "assignees": assignees,
            "body": description,
            "closed": False,
            "title": title,
        }
        result = self.allspice_client.requests_post(
            Repository.REPO_ISSUES.format(owner=self.owner.username, repo=self.name),
            data=data,
        )

        issue = Issue.parse_response(self.allspice_client, result)
        setattr(issue, "_repository", self)
        Issue._add_read_property("repo", self, issue)
        return issue

    def create_design_review(
        self,
        title: str,
        head: Union[Branch, str],
        base: Union[Branch, str],
        assignees: Optional[Set[Union[User, str]]] = None,
        body: Optional[str] = None,
        due_date: Optional[datetime] = None,
        milestone: Optional["Milestone"] = None,
    ) -> "DesignReview":
        """
        Create a new Design Review.

        See https://hub.allspice.io/api/swagger#/repository/repoCreatePullRequest

        :param title: Title of the Design Review
        :param head: Branch or name of the branch to merge into the base branch
        :param base: Branch or name of the branch to merge into
        :param assignees: Optional. A list of users to assign this review. List can be of
                          User objects or of usernames.
        :param body: An Optional Description for the Design Review.
        :param due_date: An Optional Due date for the Design Review.
        :param milestone: An Optional Milestone for the Design Review
        :return: The created Design Review
        """

        data: dict[str, Any] = {
            "title": title,
        }

        if isinstance(head, Branch):
            data["head"] = head.name
        else:
            data["head"] = head
        if isinstance(base, Branch):
            data["base"] = base.name
        else:
            data["base"] = base
        if assignees:
            data["assignees"] = [a.username if isinstance(a, User) else a for a in assignees]
        if body:
            data["body"] = body
        if due_date:
            data["due_date"] = Util.format_time(due_date)
        if milestone:
            data["milestone"] = milestone.id

        result = self.allspice_client.requests_post(
            self.REPO_DESIGN_REVIEWS.format(owner=self.owner.username, repo=self.name),
            data=data,
        )

        return DesignReview.parse_response(self.allspice_client, result)

    def create_milestone(
        self,
        title: str,
        description: str,
        due_date: Optional[str] = None,
        state: str = "open",
    ) -> "Milestone":
        url = Repository.REPO_MILESTONES.format(owner=self.owner.username, repo=self.name)
        data = {"title": title, "description": description, "state": state}
        if due_date:
            data["due_date"] = due_date
        result = self.allspice_client.requests_post(url, data=data)
        return Milestone.parse_response(self.allspice_client, result)

    def create_gitea_hook(self, hook_url: str, events: List[str]):
        url = f"/repos/{self.owner.username}/{self.name}/hooks"
        data = {
            "type": "gitea",
            "config": {"content_type": "json", "url": hook_url},
            "events": events,
            "active": True,
        }
        return self.allspice_client.requests_post(url, data=data)

    def list_hooks(self):
        url = f"/repos/{self.owner.username}/{self.name}/hooks"
        return self.allspice_client.requests_get(url)

    def delete_hook(self, id: str):
        url = f"/repos/{self.owner.username}/{self.name}/hooks/{id}"
        self.allspice_client.requests_delete(url)

    def is_collaborator(self, username) -> bool:
        if isinstance(username, User):
            username = username.username
        try:
            # returns 204 if its ok, 404 if its not
            self.allspice_client.requests_get(
                Repository.REPO_IS_COLLABORATOR % (self.owner.username, self.name, username)
            )
            return True
        except Exception:
            return False

    def get_users_with_access(self) -> Sequence[User]:
        url = f"/repos/{self.owner.username}/{self.name}/collaborators"
        response = self.allspice_client.requests_get(url)
        collabs = [User.parse_response(self.allspice_client, user) for user in response]
        if isinstance(self.owner, User):
            return [*collabs, self.owner]
        else:
            # owner must be org
            teams = self.owner.get_teams()
            for team in teams:
                team_repos = team.get_repos()
                if self.name in [n.name for n in team_repos]:
                    collabs += team.get_members()
            return collabs

    def remove_collaborator(self, user_name: str):
        url = f"/repos/{self.owner.username}/{self.name}/collaborators/{user_name}"
        self.allspice_client.requests_delete(url)

    def transfer_ownership(
        self,
        new_owner: Union[User, Organization],
        new_teams: Set[Team] | FrozenSet[Team] = frozenset(),
    ):
        url = Repository.REPO_TRANSFER.format(owner=self.owner.username, repo=self.name)
        data: dict[str, Any] = {"new_owner": new_owner.username}
        if isinstance(new_owner, Organization):
            new_team_ids = [team.id for team in new_teams if team in new_owner.get_teams()]
            data["team_ids"] = new_team_ids
        self.allspice_client.requests_post(url, data=data)
        # TODO: make sure this instance is either updated or discarded

    def get_git_content(
        self,
        ref: Optional["Ref"] = None,
        commit: "Optional[Commit]" = None,
    ) -> List[Content]:
        """
        Get the metadata for all files in the root directory.

        https://hub.allspice.io/api/swagger#/repository/repoGetContentsList

        :param ref: branch or commit to get content from
        :param commit: commit to get content from (deprecated)
        """
        url = f"/repos/{self.owner.username}/{self.name}/contents"
        data = Util.data_params_for_ref(ref or commit)

        result = [
            Content.parse_response(self.allspice_client, f)
            for f in self.allspice_client.requests_get(url, data)
        ]
        return result

    def get_tree(self, ref: Optional[Ref] = None, recursive: bool = False) -> List[GitEntry]:
        """
        Get the repository's tree on a given ref.

        By default, this will only return the top-level entries in the tree. If you want
        to get the entire tree, set `recursive` to True.

        :param ref: The ref to get the tree from. If not provided, the default branch is used.
        :param recursive: Whether to get the entire tree or just the top-level entries.
        """

        ref = Util.data_params_for_ref(ref).get("ref", self.default_branch)
        url = self.REPO_GET_TREE.format(owner=self.owner.username, repo=self.name, ref=ref)
        params = {"recursive": recursive}
        results = self.allspice_client.requests_get_paginated(url, params=params)
        return [GitEntry.parse_response(self.allspice_client, result) for result in results]

    def get_file_content(
        self,
        content: Content,
        ref: Optional[Ref] = None,
        commit: Optional[Commit] = None,
    ) -> Union[str, List["Content"]]:
        """https://hub.allspice.io/api/swagger#/repository/repoGetContents"""
        url = f"/repos/{self.owner.username}/{self.name}/contents/{content.path}"
        data = Util.data_params_for_ref(ref or commit)

        if content.type == Content.FILE:
            return self.allspice_client.requests_get(url, data)["content"]
        else:
            return [
                Content.parse_response(self.allspice_client, f)
                for f in self.allspice_client.requests_get(url, data)
            ]

    def get_raw_file(
        self,
        file_path: str,
        ref: Optional[Ref] = None,
    ) -> bytes:
        """
        Get the raw, binary data of a single file.

        Note 1: if the file you are requesting is a text file, you might want to
        use .decode() on the result to get a string. For example:

            content = repo.get_raw_file("file.txt").decode("utf-8")

        Note 2: this method will store the entire file in memory. If you want
        to download a large file, you might want to use `download_to_file`
        instead.

        See https://hub.allspice.io/api/swagger#/repository/repoGetRawFile

        :param file_path: The path to the file to get.
        :param ref: The branch or commit to get the file from.  If not provided,
            the default branch is used.
        """

        url = self.REPO_GET_RAW_FILE.format(
            owner=self.owner.username,
            repo=self.name,
            path=file_path,
        )
        params = Util.data_params_for_ref(ref)
        return self.allspice_client.requests_get_raw(url, params=params)

    def download_to_file(
        self,
        file_path: str,
        io: IO,
        ref: Optional[Ref] = None,
    ) -> None:
        """
        Download the binary data of a file to a file-like object.

        Example:

            with open("schematic.DSN", "wb") as f:
                Repository.download_to_file("Schematics/my_schematic.DSN", f)

        :param file_path: The path to the file in the repository from the root
            of the repository.
        :param io: The file-like object to write the data to.
        """

        url = self.allspice_client._AllSpice__get_url(
            self.REPO_GET_RAW_FILE.format(
                owner=self.owner.username,
                repo=self.name,
                path=file_path,
            )
        )
        params = Util.data_params_for_ref(ref)
        response = self.allspice_client.requests.get(
            url,
            params=params,
            headers=self.allspice_client.headers,
            stream=True,
        )

        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                io.write(chunk)

    def get_generated_json(self, content: Union[Content, str], ref: Optional[Ref] = None) -> dict:
        """
        Get the json blob for a cad file if it exists, otherwise enqueue
        a new job and return a 503 status.

        WARNING: This is still experimental and not recommended for critical
        applications. The structure and content of the returned dictionary can
        change at any time.

        See https://hub.allspice.io/api/swagger#/repository/repoGetAllSpiceJSON
        """

        if isinstance(content, Content):
            content = content.path

        url = self.REPO_GET_ALLSPICE_JSON.format(
            owner=self.owner.username,
            repo=self.name,
            content=content,
        )
        data = Util.data_params_for_ref(ref)
        return self.allspice_client.requests_get(url, data)

    def get_generated_svg(self, content: Union[Content, str], ref: Optional[Ref] = None) -> bytes:
        """
        Get the svg blob for a cad file if it exists, otherwise enqueue
        a new job and return a 503 status.

        WARNING: This is still experimental and not yet recommended for
        critical applications. The content of the returned svg can change
        at any time.

        See https://hub.allspice.io/api/swagger#/repository/repoGetAllSpiceSVG
        """

        if isinstance(content, Content):
            content = content.path

        url = self.REPO_GET_ALLSPICE_SVG.format(
            owner=self.owner.username,
            repo=self.name,
            content=content,
        )
        data = Util.data_params_for_ref(ref)
        return self.allspice_client.requests_get_raw(url, data)

    def get_generated_projectdata(
        self, content: Union[Content, str], ref: Optional[Ref] = None
    ) -> dict:
        """
        Get the json project data based on the cad file provided

        WARNING: This is still experimental and not yet recommended for
        critical applications. The content of the returned dictionary can change
        at any time.

        See https://hub.allspice.io/api/swagger#/repository/repoGetAllSpiceProject
        """
        if isinstance(content, Content):
            content = content.path

        url = self.REPO_GET_ALLSPICE_PROJECT.format(
            owner=self.owner.username,
            repo=self.name,
            content=content,
        )
        data = Util.data_params_for_ref(ref)
        return self.allspice_client.requests_get(url, data)

    def create_file(self, file_path: str, content: str, data: Optional[dict] = None):
        """https://hub.allspice.io/api/swagger#/repository/repoCreateFile"""
        if not data:
            data = {}
        url = f"/repos/{self.owner.username}/{self.name}/contents/{file_path}"
        data.update({"content": content})
        return self.allspice_client.requests_post(url, data)

    def change_file(self, file_path: str, file_sha: str, content: str, data: Optional[dict] = None):
        """https://hub.allspice.io/api/swagger#/repository/repoCreateFile"""
        if not data:
            data = {}
        url = f"/repos/{self.owner.username}/{self.name}/contents/{file_path}"
        data.update({"sha": file_sha, "content": content})
        return self.allspice_client.requests_put(url, data)

    def delete_file(self, file_path: str, file_sha: str, data: Optional[dict] = None):
        """https://hub.allspice.io/api/swagger#/repository/repoDeleteFile"""
        if not data:
            data = {}
        url = f"/repos/{self.owner.username}/{self.name}/contents/{file_path}"
        data.update({"sha": file_sha})
        return self.allspice_client.requests_delete(url, data)

    def get_archive(
        self,
        ref: Ref = "main",
        archive_format: ArchiveFormat = ArchiveFormat.ZIP,
    ) -> bytes:
        """
        Download all the files in a specific ref of a repository as a zip or tarball
        archive.

        https://hub.allspice.io/api/swagger#/repository/repoGetArchive

        :param ref: branch or commit to get content from, defaults to the "main" branch
        :param archive_format: zip or tar, defaults to zip
        """

        ref_string = Util.data_params_for_ref(ref)["ref"]
        url = self.REPO_GET_ARCHIVE.format(
            owner=self.owner.username,
            repo=self.name,
            ref=ref_string,
            format=archive_format.value,
        )
        return self.allspice_client.requests_get_raw(url)

    def get_topics(self) -> list[str]:
        """
        Gets the list of topics on this repository.

        See http://localhost:3000/api/swagger#/repository/repoListTopics
        """

        url = self.REPO_GET_TOPICS.format(
            owner=self.owner.username,
            repo=self.name,
        )
        return self.allspice_client.requests_get(url)["topics"]

    def add_topic(self, topic: str):
        """
        Adds a topic to the repository.

        See https://hub.allspice.io/api/swagger#/repository/repoAddTopic

        :param topic: The topic to add. Topic names must consist only of
            lowercase letters, numnbers and dashes (-), and cannot start with
            dashes. Topic names also must be under 35 characters long.
        """

        url = self.REPO_ADD_TOPIC.format(owner=self.owner.username, repo=self.name, topic=topic)
        self.allspice_client.requests_put(url)

    def create_release(
        self,
        tag_name: str,
        name: Optional[str] = None,
        body: Optional[str] = None,
        draft: bool = False,
    ):
        """
        Create a release for this repository. The release will be created for
        the tag with the given name. If there is no tag with this name, create
        the tag first.

        See https://hub.allspice.io/api/swagger#/repository/repoCreateRelease
        """

        url = self.REPO_GET_RELEASES.format(owner=self.owner.username, repo=self.name)
        data = {
            "tag_name": tag_name,
            "draft": draft,
        }
        if name is not None:
            data["name"] = name
        if body is not None:
            data["body"] = body
        response = self.allspice_client.requests_post(url, data)
        return Release.parse_response(self.allspice_client, response, self)

    def get_releases(
        self, draft: Optional[bool] = None, pre_release: Optional[bool] = None
    ) -> List[Release]:
        """
        Get the list of releases for this repository.

        See https://hub.allspice.io/api/swagger#/repository/repoListReleases
        """

        data = {}

        if draft is not None:
            data["draft"] = draft
        if pre_release is not None:
            data["pre-release"] = pre_release

        url = self.REPO_GET_RELEASES.format(owner=self.owner.username, repo=self.name)
        responses = self.allspice_client.requests_get_paginated(url, params=data)

        return [
            Release.parse_response(self.allspice_client, response, self) for response in responses
        ]

    def get_latest_release(self) -> Release:
        """
        Get the latest release for this repository.

        See https://hub.allspice.io/api/swagger#/repository/repoGetLatestRelease
        """

        url = self.REPO_GET_LATEST_RELEASE.format(owner=self.owner.username, repo=self.name)
        response = self.allspice_client.requests_get(url)
        release = Release.parse_response(self.allspice_client, response, self)
        return release

    def get_release_by_tag(self, tag: str) -> Release:
        """
        Get a release by its tag.

        See https://hub.allspice.io/api/swagger#/repository/repoGetReleaseByTag
        """

        url = self.REPO_GET_RELEASE_BY_TAG.format(
            owner=self.owner.username, repo=self.name, tag=tag
        )
        response = self.allspice_client.requests_get(url)
        release = Release.parse_response(self.allspice_client, response, self)
        return release

    def get_commit_statuses(
        self,
        commit: Union[str, Commit],
        sort: Optional[CommitStatusSort] = None,
        state: Optional[CommitStatusState] = None,
    ) -> List[CommitStatus]:
        """
        Get a list of statuses for a commit.

        This is roughly equivalent to the Commit.get_statuses method, but this
        method allows you to sort and filter commits and is more convenient if
        you have a commit SHA and don't need to get the commit itself.

        See https://hub.allspice.io/api/swagger#/repository/repoListStatuses
        """

        if isinstance(commit, Commit):
            commit = commit.sha

        params = {}
        if sort is not None:
            params["sort"] = sort.value
        if state is not None:
            params["state"] = state.value

        url = self.REPO_GET_COMMIT_STATUS.format(
            owner=self.owner.username, repo=self.name, sha=commit
        )
        response = self.allspice_client.requests_get_paginated(url, params=params)
        return [CommitStatus.parse_response(self.allspice_client, status) for status in response]

    def create_commit_status(
        self,
        commit: Union[str, Commit],
        context: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[CommitStatusState] = None,
        target_url: Optional[str] = None,
    ) -> CommitStatus:
        """
        Create a status on a commit.

        See https://hub.allspice.io/api/swagger#/repository/repoCreateStatus
        """

        if isinstance(commit, Commit):
            commit = commit.sha

        data = {}
        if context is not None:
            data["context"] = context
        if description is not None:
            data["description"] = description
        if state is not None:
            data["state"] = state.value
        if target_url is not None:
            data["target_url"] = target_url

        url = self.REPO_GET_COMMIT_STATUS.format(
            owner=self.owner.username, repo=self.name, sha=commit
        )
        response = self.allspice_client.requests_post(url, data=data)
        return CommitStatus.parse_response(self.allspice_client, response)

    def delete(self):
        self.allspice_client.requests_delete(
            Repository.REPO_DELETE % (self.owner.username, self.name)
        )
        self.deleted = True


class Milestone(ApiObject):
    allow_merge_commits: Any
    allow_rebase: Any
    allow_rebase_explicit: Any
    allow_squash_merge: Any
    archived: Any
    closed_at: Any
    closed_issues: int
    created_at: str
    default_branch: Any
    description: str
    due_on: Any
    has_issues: Any
    has_pull_requests: Any
    has_wiki: Any
    id: int
    ignore_whitespace_conflicts: Any
    name: Any
    open_issues: int
    private: Any
    state: str
    title: str
    updated_at: str
    website: Any

    API_OBJECT = """/repos/{owner}/{repo}/milestones/{number}"""  # <owner, repo>

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Milestone):
            return False
        return self.allspice_client == other.allspice_client and self.id == other.id

    def __hash__(self):
        return hash(self.allspice_client) ^ hash(self.id)

    _fields_to_parsers: ClassVar[dict] = {
        "closed_at": lambda _, t: Util.convert_time(t),
        "due_on": lambda _, t: Util.convert_time(t),
    }

    _patchable_fields: ClassVar[set[str]] = {
        "allow_merge_commits",
        "allow_rebase",
        "allow_rebase_explicit",
        "allow_squash_merge",
        "archived",
        "default_branch",
        "description",
        "has_issues",
        "has_pull_requests",
        "has_wiki",
        "ignore_whitespace_conflicts",
        "name",
        "private",
        "website",
    }

    @classmethod
    def request(cls, allspice_client, owner: str, repo: str, number: str):
        return cls._request(allspice_client, {"owner": owner, "repo": repo, "number": number})


class Attachment(ReadonlyApiObject):
    """
    An asset attached to a comment.

    You cannot edit or delete the attachment from this object - see the instance methods
    Comment.edit_attachment and delete_attachment for that.
    """

    browser_download_url: str
    created_at: str
    download_count: int
    id: int
    name: str
    size: int
    uuid: str

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Attachment):
            return False

        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)

    def download_to_file(self, io: IO):
        """
        Download the raw, binary data of this Attachment to a file-like object.

        Example:

            with open("my_file.zip", "wb") as f:
                attachment.download_to_file(f)

        :param io: The file-like object to write the data to.
        """

        response = self.allspice_client.requests.get(
            self.browser_download_url,
            headers=self.allspice_client.headers,
            stream=True,
        )
        # 4kb chunks
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                io.write(chunk)


class Comment(ApiObject):
    assets: List[Union[Any, Dict[str, Union[int, str]]]]
    body: str
    created_at: datetime
    html_url: str
    id: int
    issue_url: str
    original_author: str
    original_author_id: int
    pull_request_url: str
    updated_at: datetime
    user: User

    API_OBJECT = """/repos/{owner}/{repo}/issues/comments/{id}"""
    GET_ATTACHMENTS_PATH = """/repos/{owner}/{repo}/issues/comments/{id}/assets"""
    ATTACHMENT_PATH = """/repos/{owner}/{repo}/issues/comments/{id}/assets/{attachment_id}"""

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return False
        return self.repository == other.repository and self.id == other.id

    def __hash__(self):
        return hash(self.repository) ^ hash(self.id)

    @classmethod
    def request(cls, allspice_client, owner: str, repo: str, id: str) -> "Comment":
        return cls._request(allspice_client, {"owner": owner, "repo": repo, "id": id})

    _fields_to_parsers: ClassVar[dict] = {
        "user": lambda allspice_client, r: User.parse_response(allspice_client, r),
        "created_at": lambda _, t: Util.convert_time(t),
        "updated_at": lambda _, t: Util.convert_time(t),
    }

    _patchable_fields: ClassVar[set[str]] = {"body"}

    @property
    def parent_url(self) -> str:
        """URL of the parent of this comment (the issue or the pull request)"""

        if self.issue_url is not None and self.issue_url != "":
            return self.issue_url
        else:
            return self.pull_request_url

    @cached_property
    def repository(self) -> Repository:
        """The repository this comment was posted on."""

        owner_name, repo_name = self.parent_url.split("/")[-4:-2]
        return Repository.request(self.allspice_client, owner_name, repo_name)

    def __fields_for_path(self):
        return {
            "owner": self.repository.owner.username,
            "repo": self.repository.name,
            "id": self.id,
        }

    def commit(self):
        self._commit(self.__fields_for_path())

    def delete(self):
        self.allspice_client.requests_delete(self.API_OBJECT.format(**self.__fields_for_path()))
        self.deleted = True

    def get_attachments(self) -> List[Attachment]:
        """
        Get all attachments on this comment. This returns Attachment objects, which
        contain a link to download the attachment.

        https://hub.allspice.io/api/swagger#/issue/issueListIssueCommentAttachments
        """

        results = self.allspice_client.requests_get(
            self.GET_ATTACHMENTS_PATH.format(**self.__fields_for_path())
        )
        return [Attachment.parse_response(self.allspice_client, result) for result in results]

    def create_attachment(self, file: IO, name: Optional[str] = None) -> Attachment:
        """
        Create an attachment on this comment.

        https://hub.allspice.io/api/swagger#/issue/issueCreateIssueCommentAttachment

        :param file: The file to attach. This should be a file-like object.
        :param name: The name of the file. If not provided, the name of the file will be
                     used.
        :return: The created attachment.
        """

        args: dict[str, Any] = {
            "files": {"attachment": file},
        }
        if name is not None:
            args["params"] = {"name": name}

        result = self.allspice_client.requests_post(
            self.GET_ATTACHMENTS_PATH.format(**self.__fields_for_path()),
            **args,
        )
        return Attachment.parse_response(self.allspice_client, result)

    def edit_attachment(self, attachment: Attachment, data: dict) -> Attachment:
        """
        Edit an attachment.

        The list of params that can be edited is available at
        https://hub.allspice.io/api/swagger#/issue/issueEditIssueCommentAttachment

        :param attachment: The attachment to be edited
        :param data: The data parameter should be a dictionary of the fields to edit.
        :return: The edited attachment
        """

        args = {
            **self.__fields_for_path(),
            "attachment_id": attachment.id,
        }
        result = self.allspice_client.requests_patch(
            self.ATTACHMENT_PATH.format(**args),
            data=data,
        )
        return Attachment.parse_response(self.allspice_client, result)

    def delete_attachment(self, attachment: Attachment):
        """https://hub.allspice.io/api/swagger#/issue/issueDeleteIssueCommentAttachment"""

        args = {
            **self.__fields_for_path(),
            "attachment_id": attachment.id,
        }
        self.allspice_client.requests_delete(self.ATTACHMENT_PATH.format(**args))
        attachment.deleted = True


class Commit(ReadonlyApiObject):
    author: User
    commit: Dict[str, Union[str, Dict[str, str], Dict[str, Optional[Union[bool, str]]]]]
    committer: Dict[str, Union[int, str, bool]]
    created: str
    files: List[Dict[str, str]]
    html_url: str
    inner_commit: Dict[str, Union[str, Dict[str, str], Dict[str, Optional[Union[bool, str]]]]]
    parents: List[Union[Dict[str, str], Any]]
    sha: str
    stats: Dict[str, int]
    url: str

    API_OBJECT = """/repos/{owner}/{repo}/commits/{sha}"""
    COMMIT_GET_STATUS = """/repos/{owner}/{repo}/commits/{sha}/status"""
    COMMIT_GET_STATUSES = """/repos/{owner}/{repo}/commits/{sha}/statuses"""

    # Regex to extract owner and repo names from the url property
    URL_REGEXP = re.compile(r"/repos/([^/]+)/([^/]+)/git/commits")

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    _fields_to_parsers: ClassVar[dict] = {
        # NOTE: api may return None for commiters that are no allspice users
        "author": lambda allspice_client, u: (
            User.parse_response(allspice_client, u) if u else None
        )
    }

    def __eq__(self, other):
        if not isinstance(other, Commit):
            return False
        return self.sha == other.sha

    def __hash__(self):
        return hash(self.sha)

    @classmethod
    def parse_response(cls, allspice_client, result) -> "Commit":
        commit_cache = result["commit"]
        api_object = cls(allspice_client)
        cls._initialize(allspice_client, api_object, result)
        # inner_commit for legacy reasons
        Commit._add_read_property("inner_commit", commit_cache, api_object)
        return api_object

    def get_status(self) -> CommitCombinedStatus:
        """
        Get a combined status consisting of all statues on this commit.

        Note that the returned object is a CommitCombinedStatus object, which
        also contains a list of all statuses on the commit.

        https://hub.allspice.io/api/swagger#/repository/repoGetCommitStatus
        """

        result = self.allspice_client.requests_get(
            self.COMMIT_GET_STATUS.format(**self._fields_for_path)
        )
        return CommitCombinedStatus.parse_response(self.allspice_client, result)

    def get_statuses(self) -> List[CommitStatus]:
        """
        Get a list of all statuses on this commit.

        https://hub.allspice.io/api/swagger#/repository/repoListCommitStatuses
        """

        results = self.allspice_client.requests_get(
            self.COMMIT_GET_STATUSES.format(**self._fields_for_path)
        )
        return [CommitStatus.parse_response(self.allspice_client, result) for result in results]

    @cached_property
    def _fields_for_path(self) -> dict[str, str]:
        matches = self.URL_REGEXP.search(self.url)
        if not matches:
            raise ValueError(f"Invalid commit URL: {self.url}")

        return {
            "owner": matches.group(1),
            "repo": matches.group(2),
            "sha": self.sha,
        }


class CommitStatusState(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    FAILURE = "failure"
    WARNING = "warning"

    @classmethod
    def try_init(cls, value: str) -> CommitStatusState | str:
        """
        Try converting a string to the enum, and if that fails, return the
        string itself.
        """

        try:
            return cls(value)
        except ValueError:
            return value


class CommitStatus(ReadonlyApiObject):
    context: str
    created_at: str
    creator: User
    description: str
    id: int
    status: CommitStatusState
    target_url: str
    updated_at: str
    url: str

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    _fields_to_parsers: ClassVar[dict] = {
        # Gitea/ASH doesn't actually validate that the status is a "valid"
        # status, so we can expect empty or unknown strings in the status field.
        "status": lambda _, s: CommitStatusState.try_init(s),
        "creator": lambda allspice_client, u: (
            User.parse_response(allspice_client, u) if u else None
        ),
    }

    def __eq__(self, other):
        if not isinstance(other, CommitStatus):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class CommitCombinedStatus(ReadonlyApiObject):
    commit_url: str
    repository: Repository
    sha: str
    state: CommitStatusState
    statuses: List["CommitStatus"]
    total_count: int
    url: str

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    _fields_to_parsers: ClassVar[dict] = {
        # See CommitStatus
        "state": lambda _, s: CommitStatusState.try_init(s),
        "statuses": lambda allspice_client, statuses: [
            CommitStatus.parse_response(allspice_client, status) for status in statuses
        ],
        "repository": lambda allspice_client, r: Repository.parse_response(allspice_client, r),
    }

    def __eq__(self, other):
        if not isinstance(other, CommitCombinedStatus):
            return False
        return self.sha == other.sha

    def __hash__(self):
        return hash(self.sha)

    @classmethod
    def parse_response(cls, allspice_client, result) -> "CommitCombinedStatus":
        api_object = cls(allspice_client)
        cls._initialize(allspice_client, api_object, result)
        return api_object


class Issue(ApiObject):
    """
    An issue on a repository.

    Note: `Issue.assets` may not have any entries even if the issue has
    attachments. This happens when an issue is fetched via a bulk method like
    `Repository.get_issues`. In most cases, prefer using
    `Issue.get_attachments` to get the attachments on an issue.
    """

    assets: List[Union[Any, "Attachment"]]
    assignee: Any
    assignees: Any
    body: str
    closed_at: Any
    comments: int
    created_at: str
    due_date: Any
    html_url: str
    id: int
    is_locked: bool
    labels: List[Any]
    milestone: Optional["Milestone"]
    number: int
    original_author: str
    original_author_id: int
    pin_order: int
    pull_request: Any
    ref: str
    repository: Dict[str, Union[int, str]]
    state: str
    title: str
    updated_at: str
    url: str
    user: User

    API_OBJECT = """/repos/{owner}/{repo}/issues/{index}"""  # <owner, repo, index>
    GET_TIME = """/repos/%s/%s/issues/%s/times"""  # <owner, repo, index>
    GET_COMMENTS = """/repos/{owner}/{repo}/issues/{index}/comments"""
    CREATE_ISSUE = """/repos/{owner}/{repo}/issues"""
    GET_ATTACHMENTS = """/repos/{owner}/{repo}/issues/{index}/assets"""

    OPENED = "open"
    CLOSED = "closed"

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Issue):
            return False
        return self.repository == other.repository and self.id == other.id

    def __hash__(self):
        return hash(self.repository) ^ hash(self.id)

    _fields_to_parsers: ClassVar[dict] = {
        "milestone": lambda allspice_client, m: Milestone.parse_response(allspice_client, m),
        "user": lambda allspice_client, u: User.parse_response(allspice_client, u),
        "assets": lambda allspice_client, assets: [
            Attachment.parse_response(allspice_client, a) for a in assets
        ],
        "assignee": lambda allspice_client, u: User.parse_response(allspice_client, u),
        "assignees": lambda allspice_client, us: [
            User.parse_response(allspice_client, u) for u in us
        ],
        "state": lambda _, s: (Issue.CLOSED if s == "closed" else Issue.OPENED),
    }

    _parsers_to_fields: ClassVar[dict] = {
        "milestone": lambda m: m.id,
    }

    _patchable_fields: ClassVar[set[str]] = {
        "assignee",
        "assignees",
        "body",
        "due_date",
        "milestone",
        "state",
        "title",
    }

    def commit(self):
        args = {
            "owner": self.repository.owner.username,
            "repo": self.repository.name,
            "index": self.number,
        }
        self._commit(args)

    @classmethod
    def request(cls, allspice_client, owner: str, repo: str, number: str):
        api_object = cls._request(allspice_client, {"owner": owner, "repo": repo, "index": number})
        # The repository in the response is a RepositoryMeta object, so request
        # the full repository object and add it to the issue object.
        repository = Repository.request(allspice_client, owner, repo)
        setattr(api_object, "_repository", repository)
        # For legacy reasons
        cls._add_read_property("repo", repository, api_object)
        return api_object

    @classmethod
    def create_issue(cls, allspice_client, repo: Repository, title: str, body: str = ""):
        args = {"owner": repo.owner.username, "repo": repo.name}
        data = {"title": title, "body": body}
        result = allspice_client.requests_post(Issue.CREATE_ISSUE.format(**args), data=data)
        issue = Issue.parse_response(allspice_client, result)
        setattr(issue, "_repository", repo)
        cls._add_read_property("repo", repo, issue)
        return issue

    @property
    def owner(self) -> Organization | User:
        return self.repository.owner

    def get_time_sum(self, user: User) -> int:
        results = self.allspice_client.requests_get(
            Issue.GET_TIME % (self.owner.username, self.repository.name, self.number)
        )
        return sum(result["time"] for result in results if result and result["user_id"] == user.id)

    def get_times(self) -> Optional[Dict]:
        return self.allspice_client.requests_get(
            Issue.GET_TIME % (self.owner.username, self.repository.name, self.number)
        )

    def delete_time(self, time_id: str):
        path = f"/repos/{self.owner.username}/{self.repository.name}/issues/{self.number}/times/{time_id}"
        self.allspice_client.requests_delete(path)

    def add_time(self, time: int, created: Optional[str] = None, user_name: Optional[User] = None):
        path = f"/repos/{self.owner.username}/{self.repository.name}/issues/{self.number}/times"
        self.allspice_client.requests_post(
            path, data={"created": created, "time": int(time), "user_name": user_name}
        )

    def get_comments(self) -> List[Comment]:
        """https://hub.allspice.io/api/swagger#/issue/issueGetComments"""

        results = self.allspice_client.requests_get(
            self.GET_COMMENTS.format(
                owner=self.owner.username, repo=self.repository.name, index=self.number
            )
        )

        return [Comment.parse_response(self.allspice_client, result) for result in results]

    def create_comment(self, body: str) -> Comment:
        """https://hub.allspice.io/api/swagger#/issue/issueCreateComment"""

        path = self.GET_COMMENTS.format(
            owner=self.owner.username, repo=self.repository.name, index=self.number
        )

        response = self.allspice_client.requests_post(path, data={"body": body})
        return Comment.parse_response(self.allspice_client, response)

    def get_attachments(self) -> List[Attachment]:
        """
        Fetch all attachments on this issue.

        Unlike the assets field, this will always fetch all attachments from the
        API.

        See https://hub.allspice.io/api/swagger#/issue/issueListIssueAttachments
        """

        path = self.GET_ATTACHMENTS.format(
            owner=self.owner.username, repo=self.repository.name, index=self.number
        )
        response = self.allspice_client.requests_get(path)

        return [Attachment.parse_response(self.allspice_client, result) for result in response]

    def create_attachment(self, file: IO, name: Optional[str] = None) -> Attachment:
        """
        Create an attachment on this issue.

        https://hub.allspice.io/api/swagger#/issue/issueCreateIssueAttachment

        :param file: The file to attach. This should be a file-like object.
        :param name: The name of the file. If not provided, the name of the file will be
                     used.
        :return: The created attachment.
        """

        args: dict[str, Any] = {
            "files": {"attachment": file},
        }
        if name is not None:
            args["params"] = {"name": name}

        result = self.allspice_client.requests_post(
            self.GET_ATTACHMENTS.format(
                owner=self.owner.username, repo=self.repository.name, index=self.number
            ),
            **args,
        )

        return Attachment.parse_response(self.allspice_client, result)


class DesignReviewReviewComment(ApiObject):
    """
    A comment on a Design Review Review.
    """

    body: str
    commit_id: str
    created_at: str
    diff_hunk: str
    html_url: str
    id: int
    original_commit_id: str
    original_position: int
    path: str
    position: int
    pull_request_review_id: int
    pull_request_url: str
    resolver: Any
    sub_path: str
    updated_at: str
    user: User

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    _fields_to_parsers: ClassVar[dict] = {
        "resolver": lambda allspice_client, r: User.parse_response(allspice_client, r),
        "user": lambda allspice_client, u: User.parse_response(allspice_client, u),
    }


class DesignReviewReview(ReadonlyApiObject):
    """
    A review on a Design Review.
    """

    body: str
    comments_count: int
    commit_id: str
    dismissed: bool
    html_url: str
    id: int
    official: bool
    pull_request_url: str
    stale: bool
    state: ReviewEvent
    submitted_at: str
    team: Any
    updated_at: str
    user: User

    API_OBJECT = "/repos/{owner}/{repo}/pulls/{index}/reviews/{id}"
    GET_COMMENTS = "/repos/{owner}/{repo}/pulls/{index}/reviews/{id}/comments"

    class ReviewEvent(Enum):
        APPROVED = "APPROVED"
        PENDING = "PENDING"
        COMMENT = "COMMENT"
        REQUEST_CHANGES = "REQUEST_CHANGES"
        REQUEST_REVIEW = "REQUEST_REVIEW"
        UNKNOWN = ""

    @dataclass
    class ReviewComment:
        """
        Data required to create a review comment on a design review.

        :param body: The body of the comment.
        :param path: The path of the file to comment on. If you have a
            `Content` object, get the path using the `path` property.
        :param sub_path: The sub-path of the file to comment on. This is
            usually the page ID of the page in the multi-page document.
        :param new_position: The line number of the source code file after the
            change to add this comment on. Optional, leave unset if this is an ECAD
            file or the comment must be on the entire file.
        :param old_position: The line number of the source code file before the
            change to add this comment on. Optional, leave unset if this is an ECAD
            file or the comment must be on the entire file.
        """

        body: str
        path: str
        sub_path: Optional[str] = None
        new_position: Optional[int] = None
        old_position: Optional[int] = None

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    _fields_to_parsers: ClassVar[dict] = {
        "user": lambda allspice_client, u: User.parse_response(allspice_client, u),
        "state": lambda _, s: DesignReviewReview.ReviewEvent(s),
    }

    def _get_dr_properties(self) -> dict[str, str]:
        """
        Get the owner, repo name and design review number from the URL of this
        review's DR.
        """

        parts = self.pull_request_url.strip("/").split("/")

        try:
            index = parts[-1]
            assert parts[-2] == "pulls" or parts[-2] == "pull", (
                "Expected the second last part of the URL to be 'pulls' or 'pull', "
            )
            repo = parts[-3]
            owner = parts[-4]

            return {
                "owner": owner,
                "repo": repo,
                "index": index,
            }
        except IndexError:
            raise ValueError("Malformed design review URL: {}".format(self.pull_request_url))

    @cached_property
    def owner_name(self) -> str:
        """
        The owner of the repository this review is on.
        """

        return self._get_dr_properties()["owner"]

    @cached_property
    def repository_name(self) -> str:
        """
        The name of the repository this review is on.
        """

        return self._get_dr_properties()["repo"]

    @cached_property
    def index(self) -> str:
        """
        The index of the design review this review is on.
        """

        return self._get_dr_properties()["index"]

    def delete(self):
        """
        Delete this review.
        """

        self.allspice_client.requests_delete(
            self.API_OBJECT.format(**self._get_dr_properties(), id=self.id)
        )
        self.deleted = True

    def get_comments(self) -> List[DesignReviewReviewComment]:
        """
        Get the comments on this review.
        """

        result = self.allspice_client.requests_get(
            self.GET_COMMENTS.format(**self._get_dr_properties(), id=self.id)
        )

        return [
            DesignReviewReviewComment.parse_response(self.allspice_client, comment)
            for comment in result
        ]


class DesignReview(ApiObject):
    """
    A Design Review. See
    https://hub.allspice.io/api/swagger#/repository/repoGetPullRequest.

    Note: The base and head fields are not `Branch` objects - they are plain strings
    referring to the branch names. This is because DRs can exist for branches that have
    been deleted, which don't have an associated `Branch` object from the API. You can use
    the `Repository.get_branch` method to get a `Branch` object for a branch if you know
    it exists.
    """

    additions: Optional[int]
    allow_maintainer_edit: bool
    allow_maintainer_edits: Any
    assignee: User
    assignees: List["User"]
    base: str
    body: str
    changed_files: Optional[int]
    closed_at: Optional[str]
    comments: int
    created_at: str
    deletions: Optional[int]
    diff_url: str
    draft: bool
    due_date: Optional[str]
    head: str
    html_url: str
    id: int
    is_locked: bool
    labels: List[Any]
    merge_base: str
    merge_commit_sha: Optional[str]
    mergeable: bool
    merged: bool
    merged_at: Optional[str]
    merged_by: Any
    milestone: Any
    number: int
    patch_url: str
    pin_order: int
    repository: Optional["Repository"]
    requested_reviewers: Any
    requested_reviewers_teams: Any
    review_comments: int
    state: str
    title: str
    updated_at: str
    url: str
    user: User

    API_OBJECT = "/repos/{owner}/{repo}/pulls/{index}"
    MERGE_DESIGN_REVIEW = "/repos/{owner}/{repo}/pulls/{index}/merge"
    GET_REVIEWS = "/repos/{owner}/{repo}/pulls/{index}/reviews"
    GET_REVIEW = "/repos/{owner}/{repo}/pulls/{index}/reviews/{review_id}"
    GET_COMMENTS = "/repos/{owner}/{repo}/issues/{index}/comments"

    OPEN = "open"
    CLOSED = "closed"

    class MergeType(Enum):
        MERGE = "merge"
        REBASE = "rebase"
        REBASE_MERGE = "rebase-merge"
        SQUASH = "squash"
        MANUALLY_MERGED = "manually-merged"

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, DesignReview):
            return False
        return self.repository == other.repository and self.id == other.id

    def __hash__(self):
        return hash(self.repository) ^ hash(self.id)

    @classmethod
    def parse_response(cls, allspice_client, result) -> "DesignReview":
        api_object = super().parse_response(allspice_client, result)
        cls._add_read_property(
            "repository",
            Repository.parse_response(allspice_client, result["base"]["repo"]),
            api_object,
        )

        return api_object

    @classmethod
    def request(cls, allspice_client, owner: str, repo: str, number: str):
        """See https://hub.allspice.io/api/swagger#/repository/repoGetPullRequest"""
        return cls._request(allspice_client, {"owner": owner, "repo": repo, "index": number})

    _fields_to_parsers: ClassVar[dict] = {
        "assignee": lambda allspice_client, u: User.parse_response(allspice_client, u),
        "assignees": lambda allspice_client, us: [
            User.parse_response(allspice_client, u) for u in us
        ],
        "base": lambda _, b: b["ref"],
        "head": lambda _, h: h["ref"],
        "merged_by": lambda allspice_client, u: User.parse_response(allspice_client, u),
        "milestone": lambda allspice_client, m: Milestone.parse_response(allspice_client, m),
        "user": lambda allspice_client, u: User.parse_response(allspice_client, u),
    }

    _patchable_fields: ClassVar[set[str]] = {
        "allow_maintainer_edits",
        "assignee",
        "assignees",
        "base",
        "body",
        "due_date",
        "milestone",
        "state",
        "title",
    }

    _parsers_to_fields: ClassVar[dict] = {
        "assignee": lambda u: u.username,
        "assignees": lambda us: [u.username for u in us],
        "base": lambda b: b.name if isinstance(b, Branch) else b,
        "milestone": lambda m: m.id,
    }

    def commit(self):
        data = self.get_dirty_fields()
        if "due_date" in data and data["due_date"] is None:
            data["unset_due_date"] = True

        args = {
            "owner": self.repository.owner.username,
            "repo": self.repository.name,
            "index": self.number,
        }
        self._commit(args, data)

    def merge(self, merge_type: MergeType):
        """
        Merge the pull request. See
        https://hub.allspice.io/api/swagger#/repository/repoMergePullRequest

        :param merge_type: The type of merge to perform. See the MergeType enum.
        """

        self.allspice_client.requests_post(
            self.MERGE_DESIGN_REVIEW.format(
                owner=self.repository.owner.username,
                repo=self.repository.name,
                index=self.number,
            ),
            data={"Do": merge_type.value},
        )

    def get_comments(self) -> List[Comment]:
        """
        Get the comments on this pull request, but not specifically on a review.

        https://hub.allspice.io/api/swagger#/issue/issueGetComments

        :return: A list of comments on this pull request.
        """

        results = self.allspice_client.requests_get(
            self.GET_COMMENTS.format(
                owner=self.repository.owner.username,
                repo=self.repository.name,
                index=self.number,
            )
        )
        return [Comment.parse_response(self.allspice_client, result) for result in results]

    def create_comment(self, body: str):
        """
        Create a comment on this pull request. This uses the same endpoint as the
        comments on issues, and will not be associated with any reviews.

        https://hub.allspice.io/api/swagger#/issue/issueCreateComment

        :param body: The body of the comment.
        :return: The comment that was created.
        """

        result = self.allspice_client.requests_post(
            self.GET_COMMENTS.format(
                owner=self.repository.owner.username,
                repo=self.repository.name,
                index=self.number,
            ),
            data={"body": body},
        )
        return Comment.parse_response(self.allspice_client, result)

    def create_review(
        self,
        *,
        body: Optional[str] = None,
        event: Optional[DesignReviewReview.ReviewEvent] = None,
        comments: Optional[List[DesignReviewReview.ReviewComment]] = None,
        commit_id: Optional[str] = None,
    ) -> DesignReviewReview:
        """
        Create a review on this design review.

        https://hub.allspice.io/api/swagger#/repository/repoCreatePullRequestReview

        Note: in most cases, you should not set the body or event when creating
        a review. The event is automatically set to "PENDING" when the review
        is created. You should then use `submit_review` to submit the review
        with the desired event and body.

        :param body: The body of the review. This is the top-level comment on
            the review. If not provided, the review will be created with no body.
        :param event: The event of the review. This is the overall status of the
            review. See the ReviewEvent enum. If not provided, the API will
            default to "PENDING".
        :param comments: A list of comments on the review. Each comment should
            be a ReviewComment object. If not provided, only the base comment
            will be created.
        :param commit_id: The commit SHA to associate with the review. This is
            optional.
        """

        data: dict[str, Any] = {}

        if body is not None:
            data["body"] = body
        if event is not None:
            data["event"] = event.value
        if commit_id is not None:
            data["commit_id"] = commit_id
        if comments is not None:
            data["comments"] = [asdict(comment) for comment in comments]

        result = self.allspice_client.requests_post(
            self.GET_REVIEWS.format(
                owner=self.repository.owner.username,
                repo=self.repository.name,
                index=self.number,
            ),
            data=data,
        )

        return DesignReviewReview.parse_response(self.allspice_client, result)

    def get_reviews(self) -> List[DesignReviewReview]:
        """
        Get all reviews on this design review.

        https://hub.allspice.io/api/swagger#/repository/repoListPullReviews
        """

        results = self.allspice_client.requests_get(
            self.GET_REVIEWS.format(
                owner=self.repository.owner.username,
                repo=self.repository.name,
                index=self.number,
            )
        )

        return [
            DesignReviewReview.parse_response(self.allspice_client, result) for result in results
        ]

    def submit_review(
        self,
        review_id: int,
        event: DesignReviewReview.ReviewEvent,
        *,
        body: Optional[str] = None,
    ):
        """
        Submit a review on this design review.

        https://hub.allspice.io/api/swagger#/repository/repoSubmitPullReview

        :param review_id: The ID of the review to submit.
        :param event: The event to submit the review with. See the ReviewEvent
            enum for the possible values.
        :param body: Optional body text for the review submission.
        """

        data = {
            "event": event.value,
        }
        if body is not None:
            data["body"] = body

        result = self.allspice_client.requests_post(
            self.GET_REVIEW.format(
                owner=self.repository.owner.username,
                repo=self.repository.name,
                index=self.number,
                review_id=review_id,
            ),
            data=data,
        )

        return result


class Team(ApiObject):
    can_create_org_repo: bool
    description: str
    id: int
    includes_all_repositories: bool
    name: str
    organization: Optional["Organization"]
    permission: str
    units: List[str]
    units_map: Dict[str, str]

    API_OBJECT = """/teams/{id}"""  # <id>
    ADD_REPO = """/teams/%s/repos/%s/%s"""  # <id, org, repo>
    TEAM_DELETE = """/teams/%s"""  # <id>
    GET_MEMBERS = """/teams/%s/members"""  # <id>
    GET_REPOS = """/teams/%s/repos"""  # <id>

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Team):
            return False
        return self.organization == other.organization and self.id == other.id

    def __hash__(self):
        return hash(self.organization) ^ hash(self.id)

    _fields_to_parsers: ClassVar[dict] = {
        "organization": lambda allspice_client, o: Organization.parse_response(allspice_client, o)
    }

    _patchable_fields: ClassVar[set[str]] = {
        "can_create_org_repo",
        "description",
        "includes_all_repositories",
        "name",
        "permission",
        "units",
        "units_map",
    }

    @classmethod
    def request(cls, allspice_client, id: int):
        return cls._request(allspice_client, {"id": id})

    def commit(self):
        args = {"id": self.id}
        self._commit(args)

    def add_user(self, user: User):
        """https://hub.allspice.io/api/swagger#/organization/orgAddTeamMember"""
        url = f"/teams/{self.id}/members/{user.login}"
        self.allspice_client.requests_put(url)

    def add_repo(self, org: Organization, repo: Union[Repository, str]):
        if isinstance(repo, Repository):
            repo_name = repo.name
        else:
            repo_name = repo
        self.allspice_client.requests_put(Team.ADD_REPO % (self.id, org.username, repo_name))

    def get_members(self):
        """Get all users assigned to the team."""
        results = self.allspice_client.requests_get_paginated(
            Team.GET_MEMBERS % self.id,
        )
        return [User.parse_response(self.allspice_client, result) for result in results]

    def get_repos(self):
        """Get all repos of this Team."""
        results = self.allspice_client.requests_get(Team.GET_REPOS % self.id)
        return [Repository.parse_response(self.allspice_client, result) for result in results]

    def delete(self):
        self.allspice_client.requests_delete(Team.TEAM_DELETE % self.id)
        self.deleted = True

    def remove_team_member(self, user_name: str):
        url = f"/teams/{self.id}/members/{user_name}"
        self.allspice_client.requests_delete(url)


class Release(ApiObject):
    """
    A release on a repo.
    """

    assets: List[Union[Any, Dict[str, Union[int, str]], "ReleaseAsset"]]
    author: User
    body: str
    created_at: str
    draft: bool
    html_url: str
    id: int
    name: str
    prerelease: bool
    published_at: str
    repo: Optional["Repository"]
    repository: Optional["Repository"]
    tag_name: str
    tarball_url: str
    target_commitish: str
    upload_url: str
    url: str
    zipball_url: str

    API_OBJECT = "/repos/{owner}/{repo}/releases/{id}"
    RELEASE_CREATE_ASSET = "/repos/{owner}/{repo}/releases/{id}/assets"
    # Note that we don't strictly need the get_assets route, as the release
    # object already contains the assets.

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Release):
            return False
        return self.repo == other.repo and self.id == other.id

    def __hash__(self):
        return hash(self.repo) ^ hash(self.id)

    _fields_to_parsers: ClassVar[dict] = {
        "author": lambda allspice_client, author: User.parse_response(allspice_client, author),
    }
    _patchable_fields: ClassVar[set[str]] = {
        "body",
        "draft",
        "name",
        "prerelease",
        "tag_name",
        "target_commitish",
    }

    @classmethod
    def parse_response(cls, allspice_client, result, repo) -> Release:
        release = super().parse_response(allspice_client, result)
        Release._add_read_property("repository", repo, release)
        # For legacy reasons
        Release._add_read_property("repo", repo, release)
        setattr(
            release,
            "_assets",
            [
                ReleaseAsset.parse_response(allspice_client, asset, release)
                for asset in result["assets"]
            ],
        )
        return release

    @classmethod
    def request(
        cls,
        allspice_client,
        owner: str,
        repo: str,
        id: Optional[int] = None,
    ) -> Release:
        args = {"owner": owner, "repo": repo, "id": id}
        release_response = cls._get_gitea_api_object(allspice_client, args)
        repository = Repository.request(allspice_client, owner, repo)
        release = cls.parse_response(allspice_client, release_response, repository)
        return release

    def commit(self):
        if self.repo is None:
            raise ValueError("Cannot commit a release without a repository.")

        args = {"owner": self.repo.owner.username, "repo": self.repo.name, "id": self.id}
        self._commit(args)

    def create_asset(self, file: IO, name: Optional[str] = None) -> ReleaseAsset:
        """
        Create an asset for this release.

        https://hub.allspice.io/api/swagger#/repository/repoCreateReleaseAsset

        :param file: The file to upload. This should be a file-like object.
        :param name: The name of the file.
        :return: The created asset.
        """

        if self.repo is None:
            raise ValueError("Cannot commit a release without a repository.")

        args: dict[str, Any] = {"files": {"attachment": file}}
        if name is not None:
            args["params"] = {"name": name}

        result = self.allspice_client.requests_post(
            self.RELEASE_CREATE_ASSET.format(
                owner=self.repo.owner.username,
                repo=self.repo.name,
                id=self.id,
            ),
            **args,
        )
        return ReleaseAsset.parse_response(self.allspice_client, result, self)

    def delete(self):
        if self.repo is None:
            raise ValueError("Cannot commit a release without a repository.")

        args = {"owner": self.repo.owner.username, "repo": self.repo.name, "id": self.id}
        self.allspice_client.requests_delete(self.API_OBJECT.format(**args))
        self.deleted = True


class ReleaseAsset(ApiObject):
    browser_download_url: str
    created_at: str
    download_count: int
    id: int
    name: str
    release: Optional["Release"]
    size: int
    uuid: str

    API_OBJECT = "/repos/{owner}/{repo}/releases/{release_id}/assets/{id}"

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, ReleaseAsset):
            return False
        return self.release == other.release and self.id == other.id

    def __hash__(self):
        return hash(self.release) ^ hash(self.id)

    _fields_to_parsers: ClassVar[dict] = {}
    _patchable_fields: ClassVar[set[str]] = {
        "name",
    }

    @classmethod
    def parse_response(cls, allspice_client, result, release) -> ReleaseAsset:
        asset = super().parse_response(allspice_client, result)
        ReleaseAsset._add_read_property("release", release, asset)
        return asset

    @classmethod
    def request(
        cls,
        allspice_client,
        owner: str,
        repo: str,
        release_id: int,
        id: int,
    ) -> ReleaseAsset:
        args = {"owner": owner, "repo": repo, "release_id": release_id, "id": id}
        asset_response = cls._get_gitea_api_object(allspice_client, args)
        release = Release.request(allspice_client, owner, repo, release_id)
        asset = cls.parse_response(allspice_client, asset_response, release)
        return asset

    def commit(self):
        if self.release is None or self.release.repo is None:
            raise ValueError("Cannot commit a release asset without a release or a repository.")

        args = {
            "owner": self.release.repo.owner.username,
            "repo": self.release.repo.name,
            "release_id": self.release.id,
            "id": self.id,
        }
        self._commit(args)

    def download(self) -> bytes:
        """
        Download the raw, binary data of this asset.

        Note 1: if the file you are requesting is a text file, you might want to
        use .decode() on the result to get a string. For example:

            asset.download().decode("utf-8")

        Note 2: this method will store the entire file in memory. If you are
        downloading a large file, you might want to use download_to_file instead.
        """

        return self.allspice_client.requests.get(
            self.browser_download_url,
            headers=self.allspice_client.headers,
        ).content

    def download_to_file(self, io: IO):
        """
        Download the raw, binary data of this asset to a file-like object.

        Example:

            with open("my_file.zip", "wb") as f:
                asset.download_to_file(f)

        :param io: The file-like object to write the data to.
        """

        response = self.allspice_client.requests.get(
            self.browser_download_url,
            headers=self.allspice_client.headers,
            stream=True,
        )
        # 4kb chunks
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                io.write(chunk)

    def delete(self):
        if self.release is None or self.release.repo is None:
            raise ValueError("Cannot commit a release asset without a release or a repository.")

        args = {
            "owner": self.release.repo.owner.username,
            "repo": self.release.repo.name,
            "release_id": self.release.id,
            "id": self.id,
        }
        self.allspice_client.requests_delete(self.API_OBJECT.format(**args))
        self.deleted = True


class Content(ReadonlyApiObject):
    content: Any
    download_url: str
    encoding: Any
    git_url: str
    html_url: str
    last_commit_sha: str
    name: str
    path: str
    sha: str
    size: int
    submodule_git_url: Any
    target: Any
    type: str
    url: str

    FILE = "file"

    def __init__(self, allspice_client):
        super().__init__(allspice_client)

    def __eq__(self, other):
        if not isinstance(other, Content):
            return False

        return self.sha == other.sha and self.name == other.name

    def __hash__(self):
        return hash(self.sha) ^ hash(self.name)


Ref = Union[Branch, Commit, str]


class Util:
    @staticmethod
    def convert_time(time: str) -> datetime:
        """Parsing of strange Gitea time format ("%Y-%m-%dT%H:%M:%S:%z" but with ":" in time zone notation)"""
        try:
            return datetime.strptime(time[:-3] + "00", "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            return datetime.strptime(time[:-3] + "00", "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def format_time(time: datetime) -> str:
        """
        Format a datetime object to Gitea's time format.

        :param time: The time to format
        :return: Formatted time
        """

        return time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    @staticmethod
    def data_params_for_ref(ref: Optional[Ref]) -> Dict:
        """
        Given a "ref", returns a dict with the ref parameter for the API call.

        If the ref is None, returns an empty dict. You can pass this to the API
        directly.
        """

        if isinstance(ref, Branch):
            return {"ref": ref.name}
        elif isinstance(ref, Commit):
            return {"ref": ref.sha}
        elif ref:
            return {"ref": ref}
        else:
            return {}
