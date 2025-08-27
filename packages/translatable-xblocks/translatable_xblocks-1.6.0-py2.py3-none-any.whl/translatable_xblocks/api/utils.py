"""
Utilities, split out for easier testing & mocking.
"""


def get_course_from_modulestore(course_id):
    """
    Get course from modulestore.
    For whatever reason, this has to be a runtime import or it breaks a bunch
    of things.
    """
    # pylint: disable=import-outside-toplevel
    from xmodule.modulestore.django import modulestore

    return modulestore().get_course(course_id)
