from rest_framework import permissions, viewsets

from ichec_django_core.models import PortalFeedback

from ichec_django_core.serializers import PortalFeedbackSerializer


class PortalFeedbackViewSet(viewsets.ModelViewSet):
    queryset = PortalFeedback.objects.all()
    serializer_class = PortalFeedbackSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
