from pathlib import Path
import shutil
import os
import uuid

from django.db import models
from django.utils import timezone


class TimesStampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


def make_zip(work_path: Path, output_path: Path):
    shutil.make_archive(str(output_path), "zip", str(work_path))


def content_file_name(prefix: str, instance, filename: str):
    """
    Handler for the Django File upload_to field for user media.
    Store the media in a prefixed directory by model and
    make sure there is a unique filename
    """
    instance.original_file_name = filename
    _, ext = os.path.splitext(filename)
    return os.path.join(prefix, f"{prefix}_{uuid.uuid4()}{ext}")
