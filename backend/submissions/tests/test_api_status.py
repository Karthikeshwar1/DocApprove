from submissions.models import Status

from .helpers import ApiTestCase


class StatusUpdateTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.doc = self.make_submission(self.alice)
        self.url = f"/api/submissions/{self.doc.id}/status/"

    def patch(self, payload):
        return self.client.patch(self.url, payload, format="json")

    def test_reviewer_approves(self):
        self.login(self.rita)
        res = self.patch({"status": "approved"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "approved")
        self.assertEqual(res.data["decided_by"], "rita")
        self.assertIsNotNone(res.data["decided_at"])

    def test_reviewer_rejects(self):
        self.login(self.rita)
        self.assertEqual(self.patch({"status": "rejected"}).data["status"], "rejected")

    def test_decision_is_visible_to_submitter(self):
        self.login(self.rita)
        self.patch({"status": "approved"})
        self.login(self.alice)
        self.assertEqual(self.client.get(f"/api/submissions/{self.doc.id}/").data["status"], "approved")

    def test_second_decision_is_409(self):
        self.login(self.rita)
        self.patch({"status": "approved"})
        self.login(self.raj)
        res = self.patch({"status": "rejected"})
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.data["error"]["code"], "invalid_transition")

    def test_same_decision_twice_is_409(self):
        self.login(self.rita)
        self.patch({"status": "approved"})
        self.assertEqual(self.patch({"status": "approved"}).status_code, 409)

    def test_first_decision_is_not_overwritten_by_failed_second(self):
        self.login(self.rita)
        self.patch({"status": "approved"})
        self.patch({"status": "rejected"})
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, Status.APPROVED)
        self.assertEqual(self.doc.decided_by, self.rita)

    def test_submitter_cannot_decide_own_doc(self):
        self.login(self.alice)
        res = self.patch({"status": "approved"})
        self.assertEqual(res.status_code, 403)
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, Status.PENDING)

    def test_unauthenticated_is_401(self):
        self.assertEqual(self.patch({"status": "approved"}).status_code, 401)

    def test_pending_is_not_a_valid_target_400(self):
        self.login(self.rita)
        res = self.patch({"status": "pending"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("status", res.data["error"]["details"])

    def test_unknown_status_400(self):
        self.login(self.rita)
        self.assertEqual(self.patch({"status": "maybe"}).status_code, 400)

    def test_missing_status_400(self):
        self.login(self.rita)
        self.assertEqual(self.patch({}).status_code, 400)

    def test_wrong_type_status_400(self):
        self.login(self.rita)
        self.assertEqual(self.patch({"status": ["approved"]}).status_code, 400)

    def test_unknown_submission_404(self):
        self.login(self.rita)
        res = self.client.patch("/api/submissions/9999/status/", {"status": "approved"}, format="json")
        self.assertEqual(res.status_code, 404)

    def test_only_status_can_change(self):
        self.login(self.rita)
        self.patch({"status": "approved", "title": "Hacked"})
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.title, "Doc")

    def test_put_and_post_not_allowed(self):
        self.login(self.rita)
        self.assertEqual(self.client.put(self.url, {"status": "approved"}, format="json").status_code, 405)
        self.assertEqual(self.client.post(self.url, {"status": "approved"}, format="json").status_code, 405)
