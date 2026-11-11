import os

from rest_framework import serializers

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}
MAX_CONTENT_CHARS = 20_000


def validate_upload(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise serializers.ValidationError(f"Unsupported file type '{ext or 'none'}'. Allowed: {allowed}.")
    if file.size > MAX_FILE_BYTES:
        raise serializers.ValidationError(f"File too large (max {MAX_FILE_BYTES // (1024 * 1024)} MB).")
    if file.size == 0:
        raise serializers.ValidationError("File is empty.")
    return file
