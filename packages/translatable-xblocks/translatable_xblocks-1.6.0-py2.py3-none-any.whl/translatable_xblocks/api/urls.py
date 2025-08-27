"""API v1 URLs."""

from django.urls import path

from translatable_xblocks.api.views import ConfigAPI

urlpatterns = [
    path(
        "config/",
        ConfigAPI.as_view(),
        name="translatable-xblocks-config",
    ),
]
