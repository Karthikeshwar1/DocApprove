"""Role checks live here so any future app can reuse them."""
from rest_framework.permissions import BasePermission


class IsSubmitter(BasePermission):
    message = "Only submitters can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_submitter)


class IsReviewer(BasePermission):
    message = "Only reviewers can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_reviewer)
