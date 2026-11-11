import shutil
import tempfile

from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import Role, User
from submissions.models import Submission


class ApiTestCase(APITestCase):
    """Shared fixtures: two submitters, two reviewers, an isolated media dir."""

    @classmethod
    def setUpClass(cls):
        cls._media = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        shutil.rmtree(cls._media, ignore_errors=True)

    def setUp(self):
        self.alice = User.objects.create_user("alice", password="x", role=Role.SUBMITTER)
        self.bob = User.objects.create_user("bob", password="x", role=Role.SUBMITTER)
        self.rita = User.objects.create_user("rita", password="x", role=Role.REVIEWER)
        self.raj = User.objects.create_user("raj", password="x", role=Role.REVIEWER)

    def login(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def make_submission(self, user=None, **fields):
        fields.setdefault("title", "Doc")
        if "file" not in fields:
            fields.setdefault("content", "Some text")
        return Submission.objects.create(submitted_by=user or self.alice, **fields)
