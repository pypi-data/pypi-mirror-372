"""
Translatable versions of XBlock fields.
"""

import ast

from xblock.fields import List, String, XMLString

from translatable_xblocks.base import TranslatableXBlock


class TranslatableHTML(String):
    """
    Translatable HTML field rich content (HTML/mixed markup).

    explicitly sends mimetype='text/html' to translation service
    """

    def xt_translate(self, value, source_lang, translate_lang, xblock):
        """Translate a value to a given language. Function, defined here, allows for overriding per block."""
        return xblock.ai_translations_service.translate(
            value,
            source_lang,
            translate_lang,
            xblock.location,
            xblock.scope_ids.user_id,
            cache_override=xblock.xt_cache_behavior,
            mimetype="text/html",
        )

    def __get__(self, xblock, xblock_class):
        """
        Get the value of a string and return the translated value, if applicable.
        """
        original_value = super().__get__(xblock, xblock_class)

        # This allows get on initial definition without breaks
        if xblock is None:
            return self

        # Only operate on classes that subclass from TranslatableXBlock
        if not issubclass(xblock_class, TranslatableXBlock):
            raise AssertionError(
                f"{xblock_class} is not subclass of TranslatableXblock"
            )

        if xblock.should_translate:
            translated_value = self.xt_translate(
                original_value, xblock.source_lang, xblock.translate_lang, xblock
            )
            return translated_value

        return original_value


class TranslatableXMLString(XMLString):
    """
    Translatable String field on an XBlock with extra handling for XML processing.

    Used for fields (e.g. CAPA / Problem) that have XML definitions.
    """

    def xt_translate(self, value, source_lang, translate_lang, xblock):
        """Override translation function for XML."""
        return xblock.ai_translations_service.translate(
            value,
            source_lang,
            translate_lang,
            xblock.location,
            xblock.scope_ids.user_id,
            mimetype="text/xml",
            cache_override=xblock.xt_cache_behavior,
        )

    def __get__(self, xblock, xblock_class):
        """
        Get the value of a string and return the translated value, if applicable.
        """
        original_value = super().__get__(xblock, xblock_class)

        # This allows get on initial definition without breaks
        if xblock is None:
            return self

        # Only operate on classes that subclass from TranslatableXBlock
        if not issubclass(xblock_class, TranslatableXBlock):
            raise AssertionError(
                f"{xblock_class} is not subclass of TranslatableXblock"
            )

        if xblock.should_translate:
            translated_value = self.xt_translate(
                original_value, xblock.source_lang, xblock.translate_lang, xblock
            )
            return translated_value

        return original_value


class TranslatableString(String):
    """
    Translatable String field on an plaine text content.

    explicitly sends mimetype='text/plain' to translation service
    """

    def xt_translate(self, value, source_lang, translate_lang, xblock):
        """Translate a value to a given language. Function, defined here, allows for overriding per block."""
        return xblock.ai_translations_service.translate(
            value,
            source_lang,
            translate_lang,
            xblock.location,
            xblock.scope_ids.user_id,
            cache_override=xblock.xt_cache_behavior,
            mimetype="text/plain",
        )

    def __get__(self, xblock, xblock_class):
        """
        Get the value of a string and return the translated value, if applicable.
        """
        original_value = super().__get__(xblock, xblock_class)

        # This allows get on initial definition without breaks
        if xblock is None:
            return self

        # Only operate on classes that subclass from TranslatableXBlock
        if not issubclass(xblock_class, TranslatableXBlock):
            raise AssertionError(
                f"{xblock_class} is not subclass of TranslatableXblock"
            )

        if xblock.should_translate:
            translated_value = self.xt_translate(
                original_value, xblock.source_lang, xblock.translate_lang, xblock
            )
            return translated_value

        return original_value


class TranslatableList(List):
    """A translatable variant of a List with JSON items."""

    def xt_translate(self, value, source_lang, translate_lang, xblock):
        """Translate a value to a given language. Function, defined here, allows for overriding per block."""
        # Encode the list as a string.
        list_as_string = str(value)

        # Translate the stringified list / JSON using AI Translations
        translated_list_string = xblock.ai_translations_service.translate(
            list_as_string,
            source_lang,
            translate_lang,
            xblock.location,
            xblock.scope_ids.user_id,
            cache_override=xblock.xt_cache_behavior,
            mimetype="application/json",
        )

        # Convert the translated JSON object back to a Python list
        translated_list = ast.literal_eval(translated_list_string)
        return translated_list

    def __get__(self, xblock, xblock_class):
        """
        Get the value of a string and return the translated value, if applicable.
        """
        original_value = super().__get__(xblock, xblock_class)

        # This allows get on initial definition without breaks
        if xblock is None:
            return self

        # Only operate on classes that subclass from TranslatableXBlock
        if not issubclass(xblock_class, TranslatableXBlock):
            raise AssertionError(
                f"{xblock_class} is not subclass of TranslatableXblock"
            )

        if xblock.should_translate:
            translated_value = self.xt_translate(
                original_value, xblock.source_lang, xblock.translate_lang, xblock
            )
            return translated_value

        return original_value


TRANSLATABLE_FIELDS = [
    TranslatableHTML,
    TranslatableXMLString,
    TranslatableString,
    TranslatableList,
]
