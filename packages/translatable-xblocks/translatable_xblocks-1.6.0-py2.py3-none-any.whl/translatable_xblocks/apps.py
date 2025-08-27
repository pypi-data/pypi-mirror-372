"""
translatable_xblocks Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings, PluginURLs


class TranslatableXBlocksConfig(AppConfig):
    """
    Configuration for the translatable_xblocks Django application.
    """

    name = "translatable_xblocks"

    plugin_app = {
        PluginURLs.CONFIG: {
            "lms.djangoapp": {
                PluginURLs.NAMESPACE: "translatable_xblocks",
                PluginURLs.APP_NAME: "translatable_xblocks",
                PluginURLs.REGEX: r"^api/translatable_xblocks/",
                PluginURLs.RELATIVE_PATH: "api.urls",
            },
            "cms.djangoapp": {
                PluginURLs.NAMESPACE: "translatable_xblocks",
                PluginURLs.APP_NAME: "translatable_xblocks",
                PluginURLs.REGEX: r"^api/translatable_xblocks/",
                PluginURLs.RELATIVE_PATH: "api.urls",
            },
        },
        PluginSettings.CONFIG: {
            "lms.djangoapp": {
                "production": {
                    PluginSettings.RELATIVE_PATH: "settings.production",
                },
                "common": {
                    PluginSettings.RELATIVE_PATH: "settings.common",
                },
                "devstack": {
                    PluginSettings.RELATIVE_PATH: "settings.devstack",
                },
            },
            "cms.djangoapp": {
                "production": {
                    PluginSettings.RELATIVE_PATH: "settings.production",
                },
                "common": {
                    PluginSettings.RELATIVE_PATH: "settings.common",
                },
                "devstack": {
                    PluginSettings.RELATIVE_PATH: "settings.devstack",
                },
            },
        },
    }
