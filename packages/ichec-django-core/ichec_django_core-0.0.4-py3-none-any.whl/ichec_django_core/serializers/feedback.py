from rest_framework import serializers

from ichec_django_core.models import PortalFeedback


class PortalFeedbackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PortalFeedback
        fields = ["creator", "comments"]
        read_only_fields = ["creator"]
