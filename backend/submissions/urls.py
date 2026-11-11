from django.urls import path

from . import views

urlpatterns = [
    path("", views.SubmissionListCreateView.as_view(), name="submission-list"),
    path("<int:pk>/", views.SubmissionDetailView.as_view(), name="submission-detail"),
    path("<int:pk>/status/", views.SubmissionStatusView.as_view(), name="submission-status"),
    path("<int:pk>/file/", views.SubmissionFileView.as_view(), name="submission-file"),
]
