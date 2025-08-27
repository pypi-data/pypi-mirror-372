"""Tests for translatable XBlock fields."""

import ast
from unittest import TestCase
from unittest.mock import Mock, PropertyMock, patch

from xblock.core import XBlock
from xblock.field_data import DictFieldData

from translatable_xblocks.base import TranslatableXBlock
from translatable_xblocks.fields import (
    TranslatableHTML,
    TranslatableList,
    TranslatableString,
    TranslatableXMLString,
)


class MockTranslationService:
    """Mock translation service for testing."""

    # pylint: disable=unused-argument, too-many-positional-arguments
    def translate(
        self,
        text,
        source_lang,
        target_lang,
        location,
        user_id,
        cache_override=None,
        mimetype=None,
    ):
        """Mock implementation of the translate function."""

        # For JSON data, mock translating of json strings, but not keys
        if mimetype == "application/json":
            list_data = ast.literal_eval(text)
            translated_list = []

            for item in list_data:
                # String items directly are translated
                if isinstance(item, str):
                    translated_list.append(item)

                # Where lists are tuples (e.g. the Poll XBlock), they represent an ordered dict.
                if isinstance(item, tuple):
                    translated_tuple = []

                    for sub_item in item:
                        # A string item is a key and should not be translated
                        if isinstance(sub_item, str):
                            translated_tuple.append(sub_item)
                        # A dict should have its values, but not keys, translated
                        elif isinstance(sub_item, dict):
                            translated_tuple.append(
                                {k: f"Translated({v})" for k, v in sub_item.items()}
                            )
                    translated_list.append(tuple(translated_tuple))
            # Return value from AI Translations is a string
            return str(translated_list)

        # For HTML data, wrap in "TranslatedHTML()"
        if mimetype == "text/html":
            return f"TranslatedHTML({text})"

        # For XML data, wrap in "TranslatedXML()"
        if mimetype == "text/xml":
            return f"TranslatedXML({text})"

        # Default mock translation: wrap in "Translated()"
        return f"Translated({text})"


class TestTranslatableHTML(TestCase):
    """Tests for TranslatableHTML field."""

    @XBlock.needs("settings")
    class MockXBlock(TranslatableXBlock):
        """A mock XBlock for testing TranslatableHTML fields."""

        html_field = TranslatableHTML(default="<p>HTML Field</p>")

    def setUp(self):
        """Create a test XBlock with minimal dependencies."""
        self.scope_ids = Mock()
        self.runtime = Mock()

        # Use DictFieldData to simulate real field data behavior
        self.original_html_content = "<p>Foo Bar</p>"
        field_data = DictFieldData(
            {
                "html_field": self.original_html_content,
            }
        )

        self.block = self.MockXBlock(
            self.runtime, field_data=field_data, scope_ids=self.scope_ids
        )

        # Required fields for translation
        self.block.location = Mock()
        self.block.ai_translations_service = MockTranslationService()

        super().setUp()

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_translate_html(self, mock_should_translate):
        # Given an XBlock with TranslatableHTML field where we *should* translate.
        mock_should_translate.return_value = True

        # When I access the field
        translated = self.block.html_field

        # Then the contents is translated
        self.assertEqual(translated, f"TranslatedHTML({self.original_html_content})")

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_no_translate_html(self, mock_should_translate):
        # Given an XBlock with TranslatableHTML field where we *should not* translate.
        mock_should_translate.return_value = False

        # When I access the field
        translated = self.block.html_field

        # Then the contents is not translated
        self.assertEqual(translated, self.original_html_content)


class TestTranslatableString(TestCase):
    """Tests for TranslatableString field."""

    @XBlock.needs("settings")
    class MockXBlock(TranslatableXBlock):
        """A mock XBlock for testing TranslatableString fields."""

        string_field = TranslatableString(default="String Field")

    def setUp(self):
        """Create a test XBlock with minimal dependencies."""
        self.scope_ids = Mock()
        self.runtime = Mock()

        # Use DictFieldData to simulate real field data behavior
        self.original_string_content = "Foo Bar"
        field_data = DictFieldData(
            {
                "string_field": self.original_string_content,
            }
        )

        self.block = self.MockXBlock(
            self.runtime, field_data=field_data, scope_ids=self.scope_ids
        )

        # Required fields for translation
        self.block.location = Mock()
        self.block.ai_translations_service = MockTranslationService()

        super().setUp()

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_translate_string(self, mock_should_translate):
        # Given an XBlock with TranslatableString field where we *should* translate.
        mock_should_translate.return_value = True

        # When I access the field
        translated = self.block.string_field

        # Then the contents is translated
        self.assertEqual(translated, f"Translated({self.original_string_content})")

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_no_translate_string(self, mock_should_translate):
        # Given an XBlock with TranslatableString field where we *should not* translate.
        mock_should_translate.return_value = False

        # When I access the field
        translated = self.block.string_field

        # Then the contents is not translated
        self.assertEqual(translated, self.original_string_content)


class TestTranslatableXMLString(TestCase):
    """Tests for TranslatableXMLString field."""

    @XBlock.needs("settings")
    class MockXBlock(TranslatableXBlock):
        """A mock XBlock for testing TranslatableXMLString fields."""

        xml_field = TranslatableXMLString(default="<field>Value</field>")

    def setUp(self):
        """Create a test XBlock with minimal dependencies."""
        self.scope_ids = Mock()
        self.runtime = Mock()

        # Use DictFieldData to simulate real field data behavior
        self.original_xml_content = "<field>Foo Bar</field>"
        field_data = DictFieldData(
            {
                "xml_field": self.original_xml_content,
            }
        )

        self.block = self.MockXBlock(
            self.runtime, field_data=field_data, scope_ids=self.scope_ids
        )

        # Required fields for translation
        self.block.location = Mock()
        self.block.ai_translations_service = MockTranslationService()

        super().setUp()

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_translate_xml_string(self, mock_should_translate):
        # Given an XBlock with TranslatableXMLString field where we *should* translate.
        mock_should_translate.return_value = True

        # When I access the field
        translated = self.block.xml_field

        # Then the contents is translated
        self.assertEqual(translated, f"TranslatedXML({self.original_xml_content})")

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_no_translate_xml_string(self, mock_should_translate):
        # Given an XBlock with TranslatableXMLString field where we *should not* translate.
        mock_should_translate.return_value = False

        # When I access the field
        translated = self.block.xml_field

        # Then the contents is not translated
        self.assertEqual(translated, self.original_xml_content)


class TestTranslatableList(TestCase):
    """Tests for TranslatableList field."""

    @XBlock.needs("settings")
    class MockXBlock(TranslatableXBlock):
        """A mock XBlock for testing TranslatableXList fields."""

        # Example list field for how it's used in poll XBlocks
        list_field = TranslatableList(default=["key", {"label": "value"}])

    def setUp(self):
        """Create a test XBlock with minimal dependencies."""
        self.scope_ids = Mock()
        self.runtime = Mock()

        # Use DictFieldData to simulate real field data behavior
        self.original_list_content = [
            ("A", {"label": "Apple"}),
            ("B", {"label": "Banana"}),
            ("C", {"label": "Cherry"}),
        ]
        field_data = DictFieldData(
            {
                "list_field": self.original_list_content,
            }
        )

        self.block = self.MockXBlock(
            self.runtime, field_data=field_data, scope_ids=self.scope_ids
        )

        # Required fields for translation
        self.block.location = Mock()
        self.block.ai_translations_service = MockTranslationService()

        super().setUp()

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_translate_list(self, mock_should_translate):
        # Given an XBlock with TranslatableList field where we *should* translate.
        mock_should_translate.return_value = True

        # When I access the field
        translated = self.block.list_field

        # Then the contents is translated
        self.assertEqual(
            translated,
            [
                ("A", {"label": "Translated(Apple)"}),
                ("B", {"label": "Translated(Banana)"}),
                ("C", {"label": "Translated(Cherry)"}),
            ],
        )

    @patch.object(MockXBlock, "should_translate", new_callable=PropertyMock)
    def test_no_translate_list(self, mock_should_translate):
        # Given an XBlock with TranslatableList field where we *should not* translate.
        mock_should_translate.return_value = False

        # When I access the field
        translated = self.block.list_field

        # Then the contents is not translated
        self.assertEqual(translated, self.original_list_content)
