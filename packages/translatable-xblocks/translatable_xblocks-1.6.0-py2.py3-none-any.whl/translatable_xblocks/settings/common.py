"""Common config across environments"""


def plugin_settings(settings):
    """
    App-specific settings
    """

    # TTL in seconds for successful request to store in cache (1 day)
    settings.REQUEST_CACHE_SUCCESS_TIMEOUT = 86400

    # TTL in seconds for successful config request to store in cache (15 minutes)
    settings.CONFIG_REQUEST_CACHE_TTL = 900

    # TIL in seconds for failure request to store in cache (5 minutes)
    settings.REQUEST_CACHE_FAILURE_TIMEOUT = 300

    # Timeout in seconds for API requests
    settings.AI_TRANSLATIONS_API_TIMEOUT = 15

    # Provider type for AI transcripts
    # See ref: https://github.com/openedx/edx-val/blob/b7c5db6c95c9a8655e1f3d58429c2e52b4ead66e/edxval/models.py#L381
    settings.AI_TRANSCRIPTS_PROVIDER_TYPE = "edx_ai_translations"
