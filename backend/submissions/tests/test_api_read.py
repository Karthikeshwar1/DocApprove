from django.core.files.base import ContentFile

from submissions.models import Status
from submissions.services import decide

from .helpers import ApiTestCase

URL = "/api/submissions/"


class ListAndDetailTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.a1 = self.make_submission(self.alice, title="A1")
        self.a2 = self.make_submission(self.alice, title="A2")
        self.b1 = self.make_submission(self.bob, title="B1")

    def titles(self, res):
        return {item["title"] for item in res.data}

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(URL).status_code, 401)

    def test_submitter_sees_only_own(self):
        self.login(self.alice)
        res = self.client.get(URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.titles(res), {"A1", "A2"})

    def test_reviewer_sees_all(self):
        self.login(self.rita)
        self.assertEqual(self.titles(self.client.get(URL)), {"A1", "A2", "B1"})

    def test_newest_first(self):
        self.login(self.rita)
        ids = [item["id"] for item in self.client.get(URL).data]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_status_filter(self):
        decide(self.a1, self.rita, Status.APPROVED)
        self.login(self.rita)
        self.assertEqual(self.titles(self.client.get(URL, {"status": "approved"})), {"A1"})
        self.assertEqual(self.titles(self.client.get(URL, {"status": "pending"})), {"A2", "B1"})

    def test_status_filter_respects_visibility(self):
        self.login(self.alice)
        self.assertEqual(self.titles(self.client.get(URL, {"status": "pending"})), {"A1", "A2"})

    def test_unknown_status_filter_is_400(self):
        self.login(self.rita)
        res = self.client.get(URL, {"status": "banana"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("status", res.data["error"]["details"])

    def test_submitter_can_fetch_own(self):
        self.login(self.alice)
        res = self.client.get(f"{URL}{self.a1.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "pending")

    def test_submitter_cannot_fetch_others_doc_404_not_403(self):
        self.login(self.alice)
        self.assertEqual(self.client.get(f"{URL}{self.b1.id}/").status_code, 404)

    def test_reviewer_can_fetch_any(self):
        self.login(self.rita)
        self.assertEqual(self.client.get(f"{URL}{self.b1.id}/").status_code, 200)

    def test_unknown_id_is_404(self):
        self.login(self.rita)
        res = self.client.get(f"{URL}9999/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data["error"]["code"], "not_found")


class FileDownloadTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.doc = self.make_submission(self.alice, file=ContentFile(b"file body", name="hello.txt"))
        self.text_doc = self.make_submission(self.alice)

    def test_owner_downloads(self):
        self.login(self.alice)
        res = self.client.get(f"{URL}{self.doc.id}/file/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(b"".join(res.streaming_content), b"file body")
        self.assertIn("attachment", res["Content-Disposition"])

    def test_reviewer_downloads(self):
        self.login(self.rita)
        self.assertEqual(self.client.get(f"{URL}{self.doc.id}/file/").status_code, 200)

    def test_other_submitter_cannot_download(self):
        self.login(self.bob)
        self.assertEqual(self.client.get(f"{URL}{self.doc.id}/file/").status_code, 404)

    def test_unauthenticated_cannot_download(self):
        self.assertEqual(self.client.get(f"{URL}{self.doc.id}/file/").status_code, 401)

    def test_text_submission_has_no_file(self):
        self.login(self.alice)
        self.assertEqual(self.client.get(f"{URL}{self.text_doc.id}/file/").status_code, 404)

    def test_file_missing_on_disk_is_404(self):
        self.doc.file.delete(save=False)
        self.doc.file = "submissions/gone.txt"
        self.doc.save()
        self.login(self.alice)
        self.assertEqual(self.client.get(f"{URL}{self.doc.id}/file/").status_code, 404)
