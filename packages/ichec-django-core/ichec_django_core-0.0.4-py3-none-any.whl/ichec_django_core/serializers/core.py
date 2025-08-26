from django.contrib.auth.models import Group
from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin

from ichec_django_core.models import PortalMember, Organization


class PortalMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PortalMember
        fields = [
            "url",
            "username",
            "email",
            "first_name",
            "last_name",
            "id",
            "phone",
            "organizations",
            "is_facility_member",
        ]
        read_only_fields = [
            "is_facility_member",
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name", "id"]


class OrganizationSerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "name",
            "acronym",
            "description",
            "address",
            "website",
            "id",
            "url",
            "country",
        ]
