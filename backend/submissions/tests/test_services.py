"""Unit tests for the state machine, no HTTP involved."""
from rest_framework.exceptions import PermissionDenied

from submissions.models import Status, Submission
from submissions.services import TRANSITIONS, InvalidTransition, decide

from .helpers import ApiTestCase


class DecideTests(ApiTestCase):
    def test_pending_to_approved_records_audit_fields(self):
        sub = self.make_submission()
        result = decide(sub, self.rita, Status.APPROVED)
        self.assertEqual(result.status, Status.APPROVED)
        self.assertEqual(result.decided_by, self.rita)
        self.assertIsNotNone(result.decided_at)

    def test_pending_to_rejected(self):
        result = decide(self.make_submission(), self.rita, Status.REJECTED)
        self.assertEqual(result.status, Status.REJECTED)

    def test_terminal_states_allow_no_transition(self):
        for final in (Status.APPROVED, Status.REJECTED):
            for target in (Status.PENDING, Status.APPROVED, Status.REJECTED):
                with self.subTest(final=final, target=target):
                    sub = self.make_submission()
                    decide(sub, self.rita, final)
                    with self.assertRaises(InvalidTransition):
                        decide(sub, self.raj, target)

    def test_pending_cannot_go_back_to_pending(self):
        with self.assertRaises(InvalidTransition):
            decide(self.make_submission(), self.rita, Status.PENDING)

    def test_stale_instance_loses_the_race(self):
        """Two reviewers load the same pending doc; only the first decision wins."""
        first = self.make_submission()
        stale = Submission.objects.get(pk=first.pk)
        decide(first, self.rita, Status.APPROVED)
        with self.assertRaises(InvalidTransition):
            decide(stale, self.raj, Status.REJECTED)
        first.refresh_from_db()
        self.assertEqual(first.status, Status.APPROVED)
        self.assertEqual(first.decided_by, self.rita)

    def test_cannot_review_own_submission(self):
        # Roles are exclusive today; simulate a future where a reviewer may also submit.
        sub = self.make_submission(user=self.rita)
        with self.assertRaises(PermissionDenied):
            decide(sub, self.rita, Status.APPROVED)

    def test_every_status_is_in_the_transition_table(self):
        self.assertEqual(set(TRANSITIONS), set(Status.values))
