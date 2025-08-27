"""Tests for TranslatableXBlock base behavior"""

from unittest import TestCase
from unittest.mock import Mock, patch

import ddt

from translatable_xblocks.base import TranslatableXBlock


class MockSuperXBlock:
    """Mock XBlock for layering on translated behavior"""

    # pylint: disable=unused-argument
    def student_view(self, context, **kwargs):
        return self

    # pylint: disable=unused-argument
    def handle_ajax(self, context, **kwargs):
        return self


class MockTranslatedXBlock(TranslatableXBlock, MockSuperXBlock):
    """Mock Translated XBlock to add overridden tranlsation behavior."""


@ddt.ddt
class TestTranslatableXBlockBase(TestCase):
    """Tests for TranslatableXBlock base behavior"""

    def setUp(self):
        """Create a test block."""

        # Initialize the block
        self.scope_ids = Mock()
        self.runtime = Mock()
        self.xblock = MockTranslatedXBlock(self.runtime, scope_ids=self.scope_ids)

        # Initialize some block fields
        self.xblock.ai_translations_service = Mock()
        self.xblock.location = Mock()

        return super().setUp()

    @patch(
        "translatable_xblocks.base.TranslatableXBlocksFeatureConfig.xpert_translations_enabled_for_course"
    )
    def test_should_translate_not_enabled(self, translations_enabled):
        # Given translations are not enabled for a given scope
        translations_enabled.return_value = False

        # When I ask if we should translate
        should_translate = self.xblock.should_translate

        # Then we return False
        self.assertFalse(should_translate)

    @ddt.unpack
    @ddt.data(["en", None], [None, "ar"])
    @patch(
        "translatable_xblocks.base.TranslatableXBlocksFeatureConfig.xpert_translations_enabled_for_course"
    )
    def test_should_translate_no_language(
        self, source_lang, translate_lang, translations_enabled
    ):
        # Given translations are enabled
        translations_enabled.return_value = True

        # ... but a block isn't given a source / translate langauge
        self.xblock.source_lang = source_lang
        self.xblock.translate_lang = translate_lang

        # When I ask if we should translate
        should_translate = self.xblock.should_translate

        # Then we return False
        self.assertFalse(should_translate)

    @patch(
        "translatable_xblocks.base.TranslatableXBlocksFeatureConfig.xpert_translations_enabled_for_course"
    )
    def test_should_translate_same_language(self, translations_enabled):
        # Given translations are enabled
        translations_enabled.return_value = True

        # ... but the selected languages are the same
        self.xblock.source_lang = "en"
        self.xblock.translate_lang = "en"
        # When I ask if we should translate
        should_translate = self.xblock.should_translate

        # Then we return False
        self.assertFalse(should_translate)

    @patch(
        "translatable_xblocks.base.TranslatableXBlocksFeatureConfig.xpert_translations_enabled_for_course"
    )
    def test_should_translate(self, translations_enabled):
        # Given translations are enabled
        translations_enabled.return_value = True

        # ... and languages are allowed and different
        self.xblock.source_lang = "en"
        self.xblock.translate_lang = "gf"

        # When I ask if we should translate
        should_translate = self.xblock.should_translate

        # Then we return True
        self.assertTrue(should_translate)

    @patch.object(TranslatableXBlock, "should_translate")
    def test_student_view_untranslated(
        self, mock_should_translate
    ):  # pylint: disable=unused-argument
        # Given a translatable XBlock
        # ... where a translation is not requested
        self.xblock.should_translate = False

        # When I call the student_view
        with patch.object(MockSuperXBlock, "student_view") as super_student_view:
            context = {}
            kwargs = {"foo": "bar", "baz": "buzz"}
            self.xblock.student_view(context, **kwargs)

            # Then I return the parent block's student_view
            super_student_view.assert_called_with(context, **kwargs)

            # ... and my source / target langs are updated
            self.assertIsNone(self.xblock.source_lang)
            self.assertIsNone(self.xblock.translate_lang)

    @patch("translatable_xblocks.base.user_is_admin")
    @patch.object(TranslatableXBlock, "should_translate")
    def test_student_view_translated(
        self, mock_should_translate, mock_user_is_admin
    ):  # pylint: disable=unused-argument
        # Given a translatable XBlock
        # ... where a translation is requested
        self.xblock.should_translate = True

        # When I call the student_view
        with patch.object(MockSuperXBlock, "student_view") as super_student_view:
            context = {"src_lang": "en", "dest_lang": "gf"}
            kwargs = {"foo": "bar", "baz": "buzz"}
            self.xblock.student_view(context, **kwargs)

            # Then I return the parent block's student_view
            super_student_view.assert_called_with(context, **kwargs)

            # ... and my source / target langs are updated
            self.assertEqual(self.xblock.source_lang, "en")
            self.assertEqual(self.xblock.translate_lang, "gf")

    @patch("translatable_xblocks.base.user_is_admin")
    @patch.object(TranslatableXBlock, "should_translate")
    def test_student_view_translated_cache_reset(
        self, mock_should_translate, mock_user_is_admin
    ):  # pylint: disable=unused-argument
        # Given a translatable XBlock
        # ... where a translation is requested
        self.xblock.should_translate = True

        # When I call the student_view
        with patch.object(MockSuperXBlock, "student_view") as super_student_view:
            # ... and a cache reset is requested
            mock_user_is_admin.return_value = True
            cache_reset = {"xt_cache": "reset"}

            context = {"src_lang": "en", "dest_lang": "gf", **cache_reset}
            kwargs = {"foo": "bar", "baz": "buzz"}
            self.xblock.student_view(context, **kwargs)

            # Then I return the parent block's student_view
            super_student_view.assert_called_with(context, **kwargs)

            # ... and my source / target langs are updated
            self.assertEqual(self.xblock.source_lang, "en")
            self.assertEqual(self.xblock.translate_lang, "gf")

            # ... and cache behavior is reset after student_view
            self.assertIsNone(self.xblock.xt_cache_behavior)

    @patch.object(TranslatableXBlock, "should_translate")
    def test_handle_ajax_untranslated(
        self, mock_should_translate
    ):  # pylint: disable=unused-argument
        # Given a translatable XBlock
        # ... where a translation is NOT requested
        self.xblock.should_translate = False

        # When I call handle_ajax
        with patch.object(MockSuperXBlock, "handle_ajax") as super_handle_ajax:
            with patch.object(self.xblock, "runtime") as mock_runtime:
                dispatch = "request-name"
                data = {"foo": "bar"}
                self.xblock.handle_ajax(dispatch, data)

                # Then I call the parent block's handle_ajax with expected data
                super_handle_ajax.assert_called_once_with(dispatch, data)

                # ... and do not activate the i18n language for frontend translations
                mock_runtime.service(
                    self.xblock, "i18n"
                ).translator.activate.assert_not_called()

    @patch.object(TranslatableXBlock, "should_translate")
    def test_handle_ajax_translated(
        self, mock_should_translate
    ):  # pylint: disable=unused-argument
        # Given a translatable XBlock
        # ... where a translation is requested
        self.xblock.should_translate = True
        self.xblock.translate_lang = "gf"

        # When I call handle_ajax
        with patch.object(MockSuperXBlock, "handle_ajax") as super_handle_ajax:
            with patch.object(self.xblock, "runtime") as mock_runtime:
                dispatch = "request-name"
                data = {"foo": "bar"}
                self.xblock.handle_ajax(dispatch, data)

                # Then I call the parent block's handle_ajax with expected data
                super_handle_ajax.assert_called_once_with(dispatch, data)

                # ... and activate the i18n language for frontend translations
                mock_runtime.service(
                    self.xblock, "i18n"
                ).translator.activate.assert_called_with(self.xblock.translate_lang)
