"""
Translatable version of edx-platform/xmodule.capa_block
"""

# pylint:  disable=unnecessary-lambda-assignment

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from xblock.core import XBlock
from xblock.fields import Scope
from xmodule.capa_block import ProblemBlock as BaseProblemBlock

from translatable_xblocks.base import TranslatableXBlock
from translatable_xblocks.config import TranslatableXBlocksFeatureConfig
from translatable_xblocks.fields import TranslatableString, TranslatableXMLString

logger = logging.getLogger(__name__)

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.gettext_noop` because Django cannot be imported in this file
_ = lambda text: text


try:
    FEATURES = getattr(settings, "FEATURES", {})
except ImproperlyConfigured:
    FEATURES = {}


@XBlock.needs("user")
@XBlock.needs("i18n")
@XBlock.needs("mako")
@XBlock.needs("cache")
@XBlock.needs("sandbox")
@XBlock.needs("replace_urls")
@XBlock.wants("call_to_action")
class ProblemBlock(TranslatableXBlock, BaseProblemBlock):
    """
    Our version of the ProblemBlock with added translation logic.
    data is text/xml(application/xml) and display_name is text/plain content(mimetype)
    """

    display_name = TranslatableString(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        scope=Scope.settings,
        # it'd be nice to have a useful default but it screws up other things; so,
        # use display_name_with_default for those
        default=_("Blank Problem"),
    )

    data = TranslatableXMLString(
        help=_("XML data for the problem"),
        scope=Scope.content,
        enforce_type=FEATURES.get("ENABLE_XBLOCK_XML_VALIDATION", True),
        default="<problem></problem>",
    )

    @property
    def should_translate_feedback(self):
        """
        Determine if we should translate feedback for this context.
        """
        return (
            TranslatableXBlocksFeatureConfig.problem_block_feedback_translation_enabled(
                self.location.course_key
            )
        )

    @property
    def has_lcp_error(self):
        """
        Checks if ProblemBlock will fail on accessing its LoncapaProblem
        """
        try:
            self.lcp
        except Exception:  # lint-amnesty, pylint: disable=broad-except
            logger.info(
                f"Feedback translation not available for ProblemBlock: {self.location}"
            )
            return True
        return False

    @property
    def has_file_submissions(self):
        """
        Checks if ProblemBlock's LoncapaProblem has file submissions in its responder
        """
        for responder in self.lcp.responders.values():
            if "filesubmission" in responder.allowed_inputfields:
                logger.info(
                    f"Feedback translation not available for ProblemBlock with FileSubmission: {self.location}"
                )
                return True
        return False

    def translate_feedback(self):
        """
        Translate feedback if we should, otherwise recalculate feedback in original language
        """
        # CorrectMap is a map between answer_id and response evaluation result
        student_answers_ids = list(self.lcp.correct_map.keys())

        # If student has attempted the problem block
        if self.attempts > 0 and student_answers_ids:
            # Get key from student answer
            student_answer_id = student_answers_ids[0]

            # Get feedback for student answer to translate
            feedback = self.lcp.correct_map.get_msg(student_answer_id)

            # If feedback is not empty
            if feedback:
                # If translation behavior is enabled / selected
                if self.should_translate:
                    # Get feedback translated value
                    translated_value = self.ai_translations_service.translate(
                        feedback,
                        self.source_lang,
                        self.translate_lang,
                        self.location,
                        self.scope_ids.user_id,
                    )

                    # Update Correct Map feedback with translated result
                    self.lcp.correct_map.set_property(
                        student_answer_id, "msg", translated_value
                    )
                else:
                    # Recalculate feedback as usual
                    self.update_correctness()

    def student_view(self, context, **kwargs):
        """
        Force feedback translation if should translate, then call parent rendering.
        """

        if self.should_translate_feedback:
            # Get translation source / destination language
            self.source_lang = context.get("src_lang")
            self.translate_lang = context.get("dest_lang")

            # Only translate feedback for supported use-cases
            feedback_translation_supported = not (
                self.has_lcp_error or self.has_file_submissions
            )

            if feedback_translation_supported:
                self.translate_feedback()

        return super().student_view(context, **kwargs)
