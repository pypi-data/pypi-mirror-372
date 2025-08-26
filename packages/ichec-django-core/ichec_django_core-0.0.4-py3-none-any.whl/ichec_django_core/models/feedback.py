from django.db import models

from .core import PortalMember
from .utils import TimesStampMixin


class PortalFeedback(TimesStampMixin):

    creator = models.ForeignKey(PortalMember, on_delete=models.CASCADE)
    comments = models.TextField()
