from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from ichec_django_core.models import PortalMember, Organization

from ichec_django_core.serializers import (
    PortalMemberSerializer,
    GroupSerializer,
    OrganizationSerializer,
)


class PortalMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PortalMember.objects.all()
    serializer_class = PortalMemberSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def get_queryset(self):
        queryset = PortalMember.objects.all()
        org_id = self.request.query_params.get("organization")
        if org_id is not None:
            queryset = queryset.filter(organizations__id=org_id)
        call_id = self.request.query_params.get("call")
        if call_id is not None:
            queryset = queryset.filter(access_boards__id=call_id)
        return queryset


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def get_queryset(self):
        queryset = Group.objects.all()
        user_id = self.request.query_params.get("user")
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)
        return queryset


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class CustomAuthToken(ObtainAuthToken):

    authentication_classes: list = []

    """
    This overrides DRFs built in api auth token view
    so we return some more user details. This helps clients
    fetch the user post auth.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key, "user_id": user.pk})
