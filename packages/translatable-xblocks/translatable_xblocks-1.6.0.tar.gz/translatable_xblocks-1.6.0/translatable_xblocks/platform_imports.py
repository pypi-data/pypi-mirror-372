"""
Imports from edx-platform.

Our testing environments don't stand up entire edx-platform instances, quite reasonably,
so these imports, while available when we actually run as a plugin, don't exist for
testing. A workaround is to import these at runtime and mock this file for testing.

*Ideally* these are all things that would exist in their own libraries or abstarcted out
but, since that work hasn't been done yet, we're limited to this workaround.
"""

# pylint: disable=import-outside-toplevel


def user_is_admin(request_user):
    """
    Determine whether user is admin.

    Function uses an attribute imported from platform constants, which we could redefine but,
    for consistency, is probably better to import here.
    """
    from common.djangoapps.xblock_django.constants import ATTR_KEY_USER_IS_GLOBAL_STAFF

    return request_user.opt_attrs.get(ATTR_KEY_USER_IS_GLOBAL_STAFF)


def get_user_role(request_user, course_key):
    """
    Get the role of the current user in the course context.

    User roles are not clearly exposed outside of edx-platform, that I'm aware of.
    """
    from lms.djangoapps.courseware.access import get_user_role as platform_get_user_role

    return platform_get_user_role(request_user, course_key)


def get_platform_etree_lib():
    """
    Get platform copy of etree.

    edx-platform has a wrapper around safe_lxml to avoid XML parsing issues.
    This, however, does force us to use the platform versions of lxml and etree.
    """
    from openedx.core.lib.safe_lxml import etree as platform_etree

    return platform_etree


def course_waffle_flag(flag_name, *args, **kwargs):
    """
    Create CourseWaffleFlag model instance.

    edx-platform currently defines its own version of a WaffleFlag, scoped to a course
    to allow overrides on Course/Org level.

    Until this is broken out of platform, however, we have to use this workaround to
    enable tests to work.
    """
    from openedx.core.djangoapps.waffle_utils import CourseWaffleFlag

    # pylint: disable=toggle-missing-annotation
    return CourseWaffleFlag(flag_name, *args, **kwargs)


def import_course_waffle_flag_override():
    """
    Get the WaffleFlagCourseOverrideModel.

    edx-platform currently defines its own version of a WaffleFlag, scoped to a course
    to allow overrides on Course/Org level.

    Until this is broken out of platform, however, we have to use this workaround to
    enable tests to work.
    """
    from openedx.core.djangoapps.waffle_utils.models import (
        WaffleFlagCourseOverrideModel,
    )

    return WaffleFlagCourseOverrideModel


def get_transcript_languages_val(course_id, transcript_provider_type):
    """
    Fetch the transcript languages for a course from edxval.
    """
    from edxval.api import get_transcript_languages

    return get_transcript_languages(course_id, transcript_provider_type)
