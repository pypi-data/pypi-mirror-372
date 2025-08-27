"""
Tests of waffle.py.
"""

from unittest.mock import patch

import ddt
from django.test import TestCase

from translatable_xblocks.config import (
    WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG,
    TranslatableXBlocksFeatureConfig,
)


class MockCourseWaffle:
    """Mock CourseWaffleFlag behavior."""

    def __init__(self, enabled):
        self.enabled = enabled

    def is_enabled(self, course_key=None):  # pylint: disable=unused-argument
        return self.enabled


@ddt.ddt
class TestConfig(TestCase):
    """Tests for feature configuration / enable / disable."""

    @ddt.data(True, False)
    @patch("translatable_xblocks.config.course_waffle_flag")
    def test_whole_course_translations_available_for_course(
        self, expected_enabled, mock_course_waffle_flag
    ):
        # Given the feature is / not available for a course
        mock_course_waffle_flag.return_value = MockCourseWaffle(expected_enabled)

        # When I query for the feature being available
        actual_enabled = (
            TranslatableXBlocksFeatureConfig.xpert_translations_available_for_course(
                "some_course"
            )
        )

        # Then I get the correct result
        self.assertEqual(expected_enabled, actual_enabled)

    @ddt.unpack
    @ddt.data(
        [False, False, False],
        [False, True, False],
        [True, False, False],
        [True, True, True],
    )
    @patch("translatable_xblocks.config.course_waffle_flag")
    def test_whole_course_translations_enabled_for_course(
        self,
        available_flag_value,
        enabled_flag_value,
        expected_enabled_result,
        mock_course_waffle_flag,
    ):
        # Given the feature is / not enabled / available
        mock_course_waffle_flag.side_effect = [
            MockCourseWaffle(enabled_flag_value),
            MockCourseWaffle(available_flag_value),
        ]

        # When I query for the feature being enabled
        actual_enabled = (
            TranslatableXBlocksFeatureConfig.xpert_translations_enabled_for_course(
                "some_course"
            )
        )

        # Then I get the correct result
        # (enabled ONLY when both available and enabled are True)
        self.assertEqual(expected_enabled_result, actual_enabled)

    @patch("translatable_xblocks.config.course_waffle_flag")
    @patch("translatable_xblocks.config.import_course_waffle_flag_override")
    def test_set_xpert_translations_enabled_for_course(
        self,
        mock_waffle_flag_override,
        mock_is_available,
    ):
        # Given that the translation feature is available
        mock_is_available.is_enabled.return_value = True
        course_id = "some_course"

        # When I try to set the feature to be enabled
        TranslatableXBlocksFeatureConfig.enable_xpert_translations_for_course(
            course_id, True
        )

        # Then I set the waffle flag course override
        mock_waffle_flag_override().objects.create.assert_called_once_with(
            waffle_flag=WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG,
            course_id=course_id,
            enabled=True,
            override_choice="on",
        )

    @patch(
        "translatable_xblocks.config.TranslatableXBlocksFeatureConfig.xpert_translations_available_for_course"
    )
    @patch("translatable_xblocks.config.import_course_waffle_flag_override")
    def test_set_xpert_translations_disabled_for_course(
        self,
        mock_waffle_flag_override,
        mock_is_available,
    ):
        # Given that the translation feature is available
        mock_is_available.return_value = True
        course_id = "some_course"

        # When I try to set the feature to be disabled
        TranslatableXBlocksFeatureConfig.enable_xpert_translations_for_course(
            course_id, False
        )

        # Then I set the waffle flag course override
        mock_waffle_flag_override().objects.create.assert_called_once_with(
            waffle_flag=WHOLE_COURSE_TRANSLATIONS_ENABLED_FLAG,
            course_id=course_id,
            enabled=True,
            override_choice="off",
        )

    @patch(
        "translatable_xblocks.config.TranslatableXBlocksFeatureConfig.xpert_translations_available_for_course"
    )
    def test_set_xpert_translations_disallowed(
        self,
        mock_is_available,
    ):
        # Given that the translation feature is NOT available
        mock_is_available.return_value = False
        course_id = "some_course"

        # When I try to set the feature to be disabled
        # Then I raise an error
        with self.assertRaises(ValueError):
            TranslatableXBlocksFeatureConfig.enable_xpert_translations_for_course(
                course_id, False
            )
