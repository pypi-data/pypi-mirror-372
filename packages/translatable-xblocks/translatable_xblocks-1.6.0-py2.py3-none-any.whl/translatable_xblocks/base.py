"""
Translatable XBlock base class & utils.
"""

# pylint:  disable=no-member, unnecessary-lambda-assignment

import logging

from django.utils.translation import to_locale
from xblock.core import XBlock
from xblock.fields import Scope, String

from translatable_xblocks.ai_translations_service import AiTranslationService
from translatable_xblocks.config import TranslatableXBlocksFeatureConfig
from translatable_xblocks.platform_imports import user_is_admin

logger = logging.getLogger(__name__)

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.gettext_noop` because Django cannot be imported in this file
_ = lambda text: text


class TranslatableXBlock(XBlock):
    """
    Base block for translatable XBlocks.

    See docs/how-tos/add_a_new_xblock.rst for usage instructions.
    """

    # Translations service
    ai_translations_service = AiTranslationService()

    source_lang = String(
        display_name=_("Source Language"),
        help=_("The source language of this content."),
        scope=Scope.user_state,
    )

    translate_lang = String(
        display_name=_("Translation Language"),
        help=_("The language to translate this block into."),
        scope=Scope.user_state,
    )

    xt_cache_behavior = None

    @property
    def should_translate(self):
        """
        Determine if we should translate for this context.

        We should only translate if:
        1) Xpert Tranlsations feature is enabled for this scope.
        2) Page has a source and translate language.
        3) The language codes differ.

        NOTE - We don't check here if the languages are allowed by our course config.
        These are checked by AI Translations, which will send an error if a bad language
        code is provided.
        """
        if not TranslatableXBlocksFeatureConfig.xpert_translations_enabled_for_course(
            self.location.course_key
        ):
            return False

        if not (self.source_lang and self.translate_lang):
            return False

        return self.source_lang != self.translate_lang

    def student_view(self, context, **kwargs):
        """
        Pull translation-specific values from request context, then call parent rendering.
        """
        # Get translation source / destination language
        self.source_lang = context.get("src_lang")
        self.translate_lang = context.get("dest_lang")

        # If translation behavior is enabled / selected...
        if self.should_translate:
            # Get cache behavior overrides, only if user is admin
            user = self.runtime.service(self, "user").get_current_user()
            self.xt_cache_behavior = (
                context.get("xt_cache") if user_is_admin(user) else None
            )

            # Activate the language for this request, enables template translations
            self.runtime.service(self, "i18n").translator.activate(
                to_locale(self.translate_lang)
            )

            # Call original student_view function
            fragment = super().student_view(context, **kwargs)

            # Reset cache override requests
            self.xt_cache_behavior = None

            return fragment

        # ... otherwise, just call original student_view
        return super().student_view(context, **kwargs)

    def handle_ajax(self, dispatch, data):
        """
        Handle AJAX calls for XBlocks, called by courseware.block_render.

        Since we patch template translations per request, this other async way of getting
        a view needs to also be patched.
        """
        # If translation behavior is enabled / selected...
        if self.should_translate:
            # Activate the language for this request, enables template translations
            self.runtime.service(self, "i18n").translator.activate(
                to_locale(self.translate_lang)
            )

        return super().handle_ajax(dispatch, data)
