from django.http import FileResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsReviewer, IsSubmitter

from . import services
from .models import Status, Submission
from .serializers import StatusUpdateSerializer, SubmissionCreateSerializer, SubmissionSerializer


class VisibleSubmissionsMixin:
    """Every view scopes its queryset by role, so another user's id is just a 404."""

    def get_queryset(self):
        return Submission.objects.visible_to(self.request.user).select_related(
            "submitted_by", "decided_by"
        )


class SubmissionListCreateView(VisibleSubmissionsMixin, ListCreateAPIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        return [IsSubmitter()] if self.request.method == "POST" else [IsAuthenticated()]

    def get_serializer_class(self):
        return SubmissionCreateSerializer if self.request.method == "POST" else SubmissionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            if status not in Status.values:
                raise ValidationError({"status": [f"Must be one of: {', '.join(Status.values)}."]})
            queryset = queryset.filter(status=status)
        return queryset

    @extend_schema(
        parameters=[OpenApiParameter("status", enum=Status.values, required=False)],
        responses=SubmissionSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(request=SubmissionCreateSerializer, responses={201: SubmissionSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(submitted_by=request.user)
        return Response(SubmissionSerializer(submission).data, status=201)


class SubmissionDetailView(VisibleSubmissionsMixin, RetrieveAPIView):
    serializer_class = SubmissionSerializer


class SubmissionStatusView(VisibleSubmissionsMixin, GenericAPIView):
    """PATCH /submissions/{id}/status/ — reviewer approves or rejects."""

    permission_classes = [IsReviewer]
    serializer_class = StatusUpdateSerializer

    @extend_schema(responses=SubmissionSerializer)
    def patch(self, request, pk):
        submission = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = services.decide(submission, request.user, serializer.validated_data["status"])
        return Response(SubmissionSerializer(submission).data)


class SubmissionFileView(VisibleSubmissionsMixin, GenericAPIView):
    """GET /submissions/{id}/file/ — permission-checked download (files are never served statically)."""

    serializer_class = SubmissionSerializer

    @extend_schema(responses={(200, "application/octet-stream"): bytes})
    def get(self, request, pk):
        submission = self.get_object()
        if not submission.file:
            raise NotFound("This submission has no file.")
        try:
            handle = submission.file.open("rb")
        except FileNotFoundError:
            raise NotFound("File is no longer available.")
        return FileResponse(handle, as_attachment=True, filename=submission.file.name.rsplit("/", 1)[-1])
