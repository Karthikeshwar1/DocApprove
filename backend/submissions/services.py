"""Business rules for the approval workflow. No HTTP in here: easy to unit-test.

The state machine is a plain table. To add a state later (e.g. "changes
requested"), add it to Status and to TRANSITIONS; nothing else needs to change.
"""
from django.db import transaction
from django.utils import timezone
from rest_framework import status as http
from rest_framework.exceptions import APIException, PermissionDenied

from .models import Status, Submission

TRANSITIONS: dict[str, set[str]] = {
    Status.PENDING: {Status.APPROVED, Status.REJECTED},
    Status.APPROVED: set(),  # terminal
    Status.REJECTED: set(),  # terminal
}

# What a reviewer may set through the API (everything else is system-managed).
DECISIONS = (Status.APPROVED, Status.REJECTED)


class InvalidTransition(APIException):
    status_code = http.HTTP_409_CONFLICT
    default_code = "invalid_transition"


def decide(submission: Submission, reviewer, new_status: str) -> Submission:
    """Move a submission to `new_status`, recording who decided and when."""
    if submission.submitted_by_id == reviewer.id:
        # Unreachable while roles are exclusive; guards against future role changes.
        raise PermissionDenied("You cannot review your own submission.")

    if new_status not in TRANSITIONS[submission.status]:
        raise InvalidTransition(
            f"Cannot change status from '{submission.status}' to '{new_status}'."
        )

    now = timezone.now()
    with transaction.atomic():
        # Conditional UPDATE: only succeeds if the status is still what we read.
        # If two reviewers race, exactly one wins and the other gets a 409.
        updated = Submission.objects.filter(pk=submission.pk, status=submission.status).update(
            status=new_status, decided_by=reviewer, decided_at=now, updated_at=now
        )
    if not updated:
        submission.refresh_from_db()
        raise InvalidTransition(f"Submission was already {submission.status}.")

    submission.refresh_from_db()
    return submission
