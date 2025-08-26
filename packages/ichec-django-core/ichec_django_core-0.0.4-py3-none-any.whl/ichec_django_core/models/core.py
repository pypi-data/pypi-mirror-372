from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token
from django_countries.fields import CountryField

from .utils import TimesStampMixin


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Gives each newly created user an auth token by default
    """

    if created:
        Token.objects.create(user=instance)


class Organization(TimesStampMixin):

    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=250)
    country = CountryField()
    website = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def is_facility(self):
        return hasattr(self, "facility")


class PortalMember(User, TimesStampMixin):

    phone = models.CharField(max_length=100, blank=True, null=True)
    organizations = models.ManyToManyField(
        Organization, blank=True, related_name="members"
    )

    class Meta:
        verbose_name = "Portal Member"
        verbose_name_plural = "Portal Members"

    def __str__(self):
        return self.username

    @property
    def is_facility_member(self):
        if not self.organizations:
            return False
        for org in self.organizations.all():
            if org.is_facility:
                return True
        return False
