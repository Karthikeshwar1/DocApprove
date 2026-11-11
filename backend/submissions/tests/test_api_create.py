from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction

from submissions.models import Status, Submission
from submissions.validators import MAX_CONTENT_CHARS, MAX_FILE_BYTES

from .helpers import ApiTestCase

URL = "/api/submissions/"


class CreateSubmissionTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.alice)

    def test_create_text_submission(self):
        res = self.client.post(URL, {"title": "Report", "content": "Hello"}, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["status"], Status.PENDING)
        self.assertEqual(res.data["submitted_by"], "alice")
        self.assertIsNone(res.data["file_name"])
        self.assertEqual(Submission.objects.get().submitted_by, self.alice)

    def test_create_file_submission(self):
        f = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")
        res = self.client.post(URL, {"title": "Notes", "file": f}, format="multipart")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["file_name"], "notes.txt")

    def test_cannot_set_owner_or_status_via_payload(self):
        res = self.client.post(
            URL,
            {"title": "T", "content": "x", "status": "approved", "submitted_by": self.bob.id},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["status"], Status.PENDING)
        self.assertEqual(res.data["submitted_by"], "alice")

    def test_title_is_trimmed(self):
        res = self.client.post(URL, {"title": "  Spaced  ", "content": "x"}, format="json")
        self.assertEqual(res.data["title"], "Spaced")

    def assert_invalid(self, payload, field, fmt="json"):
        res = self.client.post(URL, payload, format=fmt)
        self.assertEqual(res.status_code, 400, res.data)
        self.assertEqual(res.data["error"]["code"], "validation_error")
        self.assertIn(field, res.data["error"]["details"])
        self.assertEqual(Submission.objects.count(), 0)

    def test_missing_title(self):
        self.assert_invalid({"content": "x"}, "title")

    def test_blank_title(self):
        self.assert_invalid({"title": "   ", "content": "x"}, "title")

    def test_title_too_long(self):
        self.assert_invalid({"title": "t" * 201, "content": "x"}, "title")

    def test_neither_content_nor_file(self):
        self.assert_invalid({"title": "T"}, "non_field_errors")

    def test_whitespace_only_content(self):
        self.assert_invalid({"title": "T", "content": "   \n "}, "non_field_errors")

    def test_both_content_and_file(self):
        f = SimpleUploadedFile("a.txt", b"hi")
        self.assert_invalid({"title": "T", "content": "x", "file": f}, "non_field_errors", "multipart")

    def test_content_too_long(self):
        self.assert_invalid({"title": "T", "content": "x" * (MAX_CONTENT_CHARS + 1)}, "content")

    def test_disallowed_file_type(self):
        f = SimpleUploadedFile("evil.exe", b"MZ")
        self.assert_invalid({"title": "T", "file": f}, "file", "multipart")

    def test_empty_file(self):
        f = SimpleUploadedFile("empty.txt", b"")
        self.assert_invalid({"title": "T", "file": f}, "file", "multipart")

    def test_file_too_large(self):
        f = SimpleUploadedFile("big.txt", b"x" * (MAX_FILE_BYTES + 1))
        self.assert_invalid({"title": "T", "file": f}, "file", "multipart")

    def test_non_object_json_body(self):
        res = self.client.post(URL, [1, 2], format="json")
        self.assertEqual(res.status_code, 400)

    def test_malformed_json(self):
        res = self.client.post(URL, "{not json", content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "parse_error")

    def test_reviewer_cannot_submit(self):
        self.login(self.rita)
        res = self.client.post(URL, {"title": "T", "content": "x"}, format="json")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["error"]["code"], "permission_denied")

    def test_unauthenticated_cannot_submit(self):
        self.client.credentials()
        res = self.client.post(URL, {"title": "T", "content": "x"}, format="json")
        self.assertEqual(res.status_code, 401)


class DatabaseInvariantTests(ApiTestCase):
    """The DB refuses states the API should never produce."""

    def test_db_rejects_content_and_file_together(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_submission(content="x", file="submissions/a.txt")

    def test_db_rejects_neither_content_nor_file(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Submission.objects.create(title="T", submitted_by=self.alice)

    def test_db_rejects_decided_status_without_decider(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_submission(status=Status.APPROVED)
