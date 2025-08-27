"""
Waffle config for the AI Translations service.
"""

import logging

from translatable_xblocks.platform_imports import (
    course_waffle_flag,
    import_course_waffle_flag_override,
)

logger = logging.getLogger(__name__)

# Waffle settings
WAFFLE_NAMESPACE = "ai_translations"
LOG_PREFIX = "AI translations: "

# .. toggle_name: WHOLE_COURSE_TRANSLATIONS
# .. toggle_implementation: CourseWaffleFlag
# .. toggle_default: False
# .. toggle_description: Enabling this flag makes the course content translation
#   feature available. Works in conjunction with WHOLE_COURSE_TRANSLATIONS_ENABLED.
# .. toggle_warning: Requires ai-translations IDA to be available
# .. toggle_use_cases: opt_in
# .. toggle_creation_date: 2024-02-27
WHOLE_COURSE_TRANSLATIONS_FLAG = f"{WAFFLE_NAMESPACE}.whole_course_translations"

# .. toggle_name: WHOLE_COURSE_TRANSLATIONS_ENABLED
# .. toggle_implementation: CourseWaffleFlag
# .. toggle_default: False
# .. toggle_description: Enabling this feature allows course content to be sent to the
#   AI Translations service for automatic translation of course content.
# .. toggle_warning: Requires ai-translations IDA to be available
# .. toggle_use_cases: opt_in
# .. toggle_creation_date: 2024-05-09
WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG = (
    f"{WAFFLE_NAMESPACE}.whole_course_translations_enabled"
)

# .. toggle_name: PROBLEM_BLOCK_FEEDBACK_TRANSLATION
# .. toggle_implementation: CourseWaffleFlag
# .. toggle_default: False
# .. toggle_description: Enabling this feature allows ProblemBlock feedback to be translated
# .. toggle_warning: Requires ai-translations IDA to be available
# .. toggle_use_cases: opt_in
# .. toggle_creation_date: 2024-27-09
PROBLEM_BLOCK_FEEDBACK_TRANSLATION_FLAG = (
    f"{WAFFLE_NAMESPACE}.problem_block_feedback_translation"
)


class TranslatableXBlocksFeatureConfig:
    """Class containing configuration information about Translations features."""

    @staticmethod
    def xpert_translations_available_for_course(course_key):
        """
        Determine if the Xpert translation feature is available for the given context.

        Feature is considered "available" if we have the WHOLE_COURSE_TRANSLATIONS_FLAG
        enabled for that context.
        """
        xpert_translations_available_setting = course_waffle_flag(
            WHOLE_COURSE_TRANSLATIONS_FLAG, __name__, LOG_PREFIX
        )
        return xpert_translations_available_setting.is_enabled(course_key=course_key)

    @staticmethod
    def xpert_translations_enabled_for_course(course_key):
        """
        Determine if the Xpert translation feature is enabled for the given context.

        Feature is considered "enabled" if the following are both true:
        1) Feature is available
        2) Feature is enabled
        """
        xpert_translations_enabled_setting = course_waffle_flag(
            WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG, __name__, LOG_PREFIX
        )

        return TranslatableXBlocksFeatureConfig.xpert_translations_available_for_course(
            course_key
        ) and xpert_translations_enabled_setting.is_enabled(course_key=course_key)

    @staticmethod
    def problem_block_feedback_translation_enabled(course_key):
        """
        Determine if the ProblemBlock feedback translation feature is available for the given context.

        Feature is considered "enabled" if we have the PROBLEM_BLOCK_FEEDBACK_TRANSLATION_FLAG
        enabled for that context.
        """
        problem_block_feedback_translation = course_waffle_flag(
            PROBLEM_BLOCK_FEEDBACK_TRANSLATION_FLAG, __name__, LOG_PREFIX
        )
        return problem_block_feedback_translation.is_enabled(course_key=course_key)

    @staticmethod
    def enable_xpert_translations_for_course(course_key, enabled):
        """
        Set the waffle flag programatically for a course.

        Raises: ValueError if trying to modify "enabled" when feature not available.
        """
        # Shorthand to be less verbose
        config = TranslatableXBlocksFeatureConfig

        if not config.xpert_translations_available_for_course(course_key):
            err_string = (
                f"Cannot set {WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG}"
                f"when {WHOLE_COURSE_TRANSLATIONS_FLAG} is not enabled"
            )
            logger.error(err_string)
            raise ValueError(err_string)

        # Runtime import to allow tests to work
        WaffleFlagCourseOverrideModel = import_course_waffle_flag_override()

        WaffleFlagCourseOverrideModel.objects.create(
            waffle_flag=WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG,
            course_id=course_key,
            enabled=True,
            override_choice="on" if enabled else "off",
        )

        logger.info(
            f"Set {WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG} "
            f'to {"enabled" if enabled else "disabled"} '
            f"for course {str(course_key)}"
        )
