"""Config specific to the developer environment"""


def plugin_settings(settings):
    """
    App-specific settings
    """
    # AI Translations Service
    settings.AI_TRANSLATIONS_API_URL = "http://host.docker.internal:18760"
    settings.AI_TRANSLATIONS_OAUTH_APP_NAME = "ai_translations-backend-service"

    # Add filter config
    settings.OPEN_EDX_FILTERS_CONFIG = getattr(settings, "OPEN_EDX_FILTERS_CONFIG", {})

    settings.OPEN_EDX_FILTERS_CONFIG[
        "org.openedx.learning.xblock.render.started.v1"
    ] = {
        "fail_silently": False,
        "pipeline": ["translatable_xblocks.filters.UpdateRequestLanguageCode"],
    }

    # Cache Settings (shorter, ease of development)

    # TTL in seconds for successful request to store in cache (5 minutes)
    settings.REQUEST_CACHE_SUCCESS_TIMEOUT = 300

    # TTL in seconds for successful config request to store in cache (1 minute)
    settings.CONFIG_REQUEST_CACHE_TTL = 60

    # TIL in seconds for failure request to store in cache (30 seconds)
    settings.REQUEST_CACHE_FAILURE_TIMEOUT = 30

    # Timeout in seconds for API requests
    settings.AI_TRANSLATIONS_API_TIMEOUT = 15
