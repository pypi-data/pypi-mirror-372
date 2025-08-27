"""Tests for translatable_xblocks/util.py"""

from unittest import TestCase

from translatable_xblocks.utils import (
    reinsert_base64_images,
    replace_img_base64_with_placeholder,
)


class TestBase64ImageReplacement(TestCase):
    """Tests for replacing base64 images with placeholders."""

    def test_base64_image_replace(self):
        text = (
            "<p>Here is an image:</p>"
            '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA" alt="Example">'
            "<p>Another paragraph.</p>"
            '<img src="data:image/jpg;base64,iBlahBlahBlah" alt="Example2">'
        )

        expected_text = (
            '<p>Here is an image:</p><img src="BASE64_IMG_PLACEHOLDER_0" alt="Example">'
            '<p>Another paragraph.</p><img src="BASE64_IMG_PLACEHOLDER_1" alt="Example2">'
        )

        replaced_text, base64_images = replace_img_base64_with_placeholder(text)

        self.assertEqual(expected_text, replaced_text)
        self.assertEqual(len(base64_images), 2)

        actual_text = reinsert_base64_images(replaced_text, base64_images)
        self.assertEqual(actual_text, text)
