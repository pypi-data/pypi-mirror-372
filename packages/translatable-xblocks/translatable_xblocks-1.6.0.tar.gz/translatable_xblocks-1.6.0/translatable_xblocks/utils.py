"""
Utilities used across the Translatable XBlocks Repo.
"""

import re


def replace_img_base64_with_placeholder(content):
    """
    Replace base64 images with placeholder.

    This is needed to prevent the code from sending huge amount of text to Google
    as base64 images are usually single long strings that exceeds Google translate limit.
    """
    base64_images = []
    placeholder_template = "BASE64_IMG_PLACEHOLDER_{index}"

    # Function to replace base64 src with placeholders
    def replace_match(match):
        base64_images.append((match.group(3), match.group(4)))
        placeholder = placeholder_template.format(index=len(base64_images) - 1)
        return f'<img {match.group(1)}src="{placeholder}"'

    # Regex to find <img> tags with base64 src
    img_tag_regex = (
        r'<img\s+([^>]*?)src=(["\'])data:image/(png|jpeg|jpg|gif);base64,([^"\']+)\2'
    )
    processed_content = re.sub(img_tag_regex, replace_match, content)

    return processed_content, base64_images


def reinsert_base64_images(content, base64_images):
    """Replace placeholders with the original base64 string."""
    for index, (image_type, base64_str) in enumerate(base64_images):
        placeholder = f"BASE64_IMG_PLACEHOLDER_{index}"
        content = content.replace(
            placeholder, f"data:image/{image_type};base64,{base64_str}"
        )
    return content
