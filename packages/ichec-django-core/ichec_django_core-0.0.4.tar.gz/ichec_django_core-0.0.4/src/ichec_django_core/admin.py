# Register your models here.
from django.contrib import admin

from .models import PortalMember, Organization

admin.site.register(PortalMember)
admin.site.register(Organization)
