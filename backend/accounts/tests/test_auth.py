from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Role, User


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user("alice", password="pw12345", role=Role.SUBMITTER)

    def test_login_returns_token_and_user(self):
        res = self.client.post("/api/auth/login/", {"username": "alice", "password": "pw12345"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["token"])
        self.assertEqual(res.data["user"]["role"], "submitter")

    def test_wrong_password_is_400_with_generic_message(self):
        res = self.client.post("/api/auth/login/", {"username": "alice", "password": "nope"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "validation_error")

    def test_unknown_user_gives_same_error_as_wrong_password(self):
        bad_pw = self.client.post("/api/auth/login/", {"username": "alice", "password": "nope"})
        no_user = self.client.post("/api/auth/login/", {"username": "ghost", "password": "nope"})
        self.assertEqual(bad_pw.data, no_user.data)

    def test_missing_fields_is_400(self):
        res = self.client.post("/api/auth/login/", {})
        self.assertEqual(res.status_code, 400)
        self.assertIn("username", res.data["error"]["details"])

    def test_me_requires_token(self):
        res = self.client.get("/api/auth/me/")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data["error"]["code"], "not_authenticated")

    def test_me_returns_current_user(self):
        login = self.client.post("/api/auth/login/", {"username": "alice", "password": "pw12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        self.assertEqual(self.client.get("/api/auth/me/").data["username"], "alice")
