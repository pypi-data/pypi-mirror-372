"""
Translatable version of edx-platform/xmodule/video_block
"""

from xblock.core import XBlock
from xblock.fields import Scope
from xmodule.video_block import VideoBlock as BaseVideoBlock

from translatable_xblocks.base import TranslatableXBlock
from translatable_xblocks.fields import TranslatableString

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.gettext_noop` because Django cannot be imported in this file
_ = lambda text: text  # pylint:  disable=unnecessary-lambda-assignment


@XBlock.wants("settings", "completion", "i18n", "request_cache")
@XBlock.needs("mako", "user")
class VideoBlock(TranslatableXBlock, BaseVideoBlock):
    """
    Only translate display_name which is plain text
    """

    display_name = TranslatableString(
        help=_("The display name for this component."),
        display_name=_("Component Display Name"),
        default="Video",
        scope=Scope.settings,
    )
