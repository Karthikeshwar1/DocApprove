from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    SUBMITTER = "submitter", "Submitter"
    REVIEWER = "reviewer", "Reviewer"


class User(AbstractUser):
    """Custom user from day one (cheap now, painful to swap later).

    A user has exactly one role. Roles are exclusive, so a reviewer can never
    review their own submission.
    """

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SUBMITTER)

    @property
    def is_reviewer(self) -> bool:
        return self.role == Role.REVIEWER

    @property
    def is_submitter(self) -> bool:
        return self.role == Role.SUBMITTER
