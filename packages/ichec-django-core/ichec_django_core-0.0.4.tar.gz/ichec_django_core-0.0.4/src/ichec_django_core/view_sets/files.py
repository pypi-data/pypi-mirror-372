import importlib
import uuid
import os
from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.request import Request
from rest_framework.permissions import (
    DjangoObjectPermissions,
    IsAuthenticated,
    DjangoModelPermissions,
)
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from django_downloadview import ObjectDownloadView

rest_auth = importlib.import_module("rest_framework.authentication")

_AUTH_CLASSES = []
for c in settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]:
    modname = ".".join(c.split(".")[:-1])
    mod = importlib.import_module(modname)
    _AUTH_CLASSES.append(getattr(mod, c.split(".")[-1]))


class ObjectFileUploadView(GenericAPIView):

    parser_classes = [FileUploadParser]
    permission_classes = [
        IsAuthenticated,
        DjangoModelPermissions,
    ]

    def put(self, request, *args, **kwargs):

        field_path = f"{self.model._meta.model_name}_{self.file_field}"
        os.makedirs(Path(settings.MEDIA_ROOT) / field_path, exist_ok=True)

        filename = request.data["file"].name

        _, ext = os.path.splitext(filename)
        file_path = f"{field_path}_{uuid.uuid4()}{ext}"
        media_path = Path(settings.MEDIA_ROOT) / field_path
        written_path = FileSystemStorage(location=media_path).save(
            file_path, request.data["file"]
        )

        instance = self.get_object()
        getattr(instance, self.file_field).name = os.path.join(field_path, written_path)
        instance.save()

        return Response(status=204)


class ObjectFileDownloadView(ObjectDownloadView):

    permissions_class = DjangoObjectPermissions

    def authenticate(self, request) -> None:
        for auth_class in _AUTH_CLASSES:
            auth_resp = auth_class().authenticate(Request(request))
            if auth_resp is not None:
                request.user = auth_resp[0]
                return

    def has_permission(self, request) -> None:

        instance = self.get_object()
        permissions = self.permissions_class()
        if not (
            permissions.has_permission(request, self)
            and permissions.has_object_permission(request, self, instance)
        ):
            raise PermissionDenied()

    def get(self, request, *args, **kwargs):
        self.authenticate(request)
        self.has_permission(request)
        return super().get(request, *args, **kwargs)
