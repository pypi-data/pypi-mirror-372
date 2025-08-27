"""
Translatable version of edx-platform/xmodule.html_block
"""

# pylint:  disable=unnecessary-lambda-assignment

from xblock.core import XBlock
from xblock.fields import Scope
from xmodule.html_block import HtmlBlock as OverriddenHtmlBlock

from translatable_xblocks.base import TranslatableXBlock
from translatable_xblocks.fields import TranslatableHTML

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.gettext_noop` because Django cannot be imported in this file
_ = lambda text: text


@XBlock.needs("i18n")
@XBlock.needs("mako")
@XBlock.needs("user")
class HtmlBlock(TranslatableXBlock, OverriddenHtmlBlock):
    """
    Translatable version of the HtmlBlock.

    Here, we only have to translate the data field.
    """

    data = TranslatableHTML(
        help=_("Html contents to display for this block"),
        default="",
        scope=Scope.content,
    )

    @XBlock.supports("multi_device")
    def student_view(self, context, **kwargs):
        return super().student_view(context, **kwargs)
