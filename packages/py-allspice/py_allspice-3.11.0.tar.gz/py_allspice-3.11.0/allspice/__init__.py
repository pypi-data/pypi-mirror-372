"""
.. include:: ../README.md
   :start-line: 1
   :end-before: Installation
"""

from .allspice import (
    AllSpice,
)
from .apiobject import (
    Branch,
    Comment,
    Commit,
    Content,
    DesignReview,
    DesignReviewReview,
    Issue,
    Milestone,
    Organization,
    Release,
    Repository,
    Team,
    User,
)
from .exceptions import AlreadyExistsException, NotFoundException

__version__ = "3.11.0"

__all__ = [
    "AllSpice",
    "AlreadyExistsException",
    "Branch",
    "Comment",
    "Commit",
    "Content",
    "DesignReview",
    "DesignReviewReview",
    "Issue",
    "Milestone",
    "NotFoundException",
    "Organization",
    "Release",
    "Repository",
    "Team",
    "User",
]
