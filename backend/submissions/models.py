from django.conf import settings
from django.db import models
from django.db.models import Q


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class SubmissionQuerySet(models.QuerySet):
    def visible_to(self, user):
        """Reviewers see everything; submitters only their own."""
        if user.is_reviewer:
            return self
        return self.filter(submitted_by=user)


class Submission(models.Model):
    title = models.CharField(max_length=200)
    # A document is either pasted text or an uploaded file (enforced below).
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="submissions/%Y/%m/", blank=True, max_length=255)

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submissions"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Audit trail: who decided and when. Both null while pending.
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="decisions",
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    objects = SubmissionQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            # Invariants live in the DB too, so no code path can break them.
            models.CheckConstraint(
                name="submission_has_content_xor_file",
                condition=(~Q(content="") & Q(file="")) | (Q(content="") & ~Q(file="")),
            ),
            models.CheckConstraint(
                name="submission_decision_matches_status",
                condition=Q(status=Status.PENDING, decided_by__isnull=True, decided_at__isnull=True)
                | (~Q(status=Status.PENDING) & Q(decided_by__isnull=False, decided_at__isnull=False)),
            ),
        ]

    def __str__(self):
        return f"#{self.pk} {self.title} [{self.status}]"
