from rest_framework import serializers

from .models import Status, Submission
from .services import DECISIONS
from .validators import MAX_CONTENT_CHARS, validate_upload


class SubmissionSerializer(serializers.ModelSerializer):
    """Read shape. The file itself is fetched via /submissions/{id}/file/."""

    submitted_by = serializers.CharField(source="submitted_by.username")
    decided_by = serializers.CharField(source="decided_by.username", default=None)
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id", "title", "content", "file_name", "status",
            "submitted_by", "created_at", "decided_by", "decided_at",
        ]
        read_only_fields = fields

    def get_file_name(self, obj) -> str | None:
        return obj.file.name.rsplit("/", 1)[-1] if obj.file else None


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Write shape: a title plus exactly one of `content` or `file`."""

    content = serializers.CharField(required=False, allow_blank=True, max_length=MAX_CONTENT_CHARS)
    file = serializers.FileField(required=False, validators=[validate_upload])

    class Meta:
        model = Submission
        fields = ["title", "content", "file"]

    def validate(self, attrs):
        has_content = bool(attrs.get("content", "").strip())
        has_file = attrs.get("file") is not None
        if has_content == has_file:  # both or neither
            raise serializers.ValidationError(
                "Provide exactly one of 'content' or 'file'.", code="content_xor_file"
            )
        return attrs


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[s for s in Status if s in DECISIONS],
        error_messages={"invalid_choice": "Status must be 'approved' or 'rejected'."},
    )
