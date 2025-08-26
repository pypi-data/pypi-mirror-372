from django.urls import include, path
from django.contrib import admin
from django.conf import settings

from .view_sets import (
    PortalMemberViewSet,
    GroupViewSet,
    OrganizationViewSet,
    PortalFeedbackViewSet,
    CustomAuthToken,
)


def register_drf_views(router):
    router.register(r"groups", GroupViewSet)
    router.register(r"organizations", OrganizationViewSet)
    router.register(r"members", PortalMemberViewSet)
    router.register(r"portal_feeedback", PortalFeedbackViewSet)
    return router


urlpatterns = [
    path("api-token-auth/", CustomAuthToken.as_view()),
    path(f"{settings.API_AUTH_URL}/", include("rest_framework.urls")),
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
]

if settings.WITH_OIDC:
    urlpatterns += [path("oidc/", include("mozilla_django_oidc.urls"))]
