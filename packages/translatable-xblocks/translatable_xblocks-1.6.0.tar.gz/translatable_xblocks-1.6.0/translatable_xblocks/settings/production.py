"""Config specific to the production environment"""


def plugin_settings(settings):
    """
    App-specific settings
    """

    settings.AI_TRANSLATIONS_OAUTH_APP_NAME = "ai-translations-backend-service"
