"""
Translatable version of Poll XBlock.
"""

# pylint:  disable=unnecessary-lambda-assignment

import importlib.resources
import inspect

from poll import PollBlock as OverriddenPollBlock
from xblock.core import XBlock
from xblock.fields import Scope

from translatable_xblocks.base import TranslatableXBlock
from translatable_xblocks.fields import TranslatableList, TranslatableString

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.gettext_noop` because Django cannot be imported in this file
_ = lambda text: text


@XBlock.needs("i18n")
@XBlock.needs("settings")
@XBlock.needs("user")
class PollBlock(TranslatableXBlock, OverriddenPollBlock):
    """
    Translatable version of the PollBlock.
    """

    @classmethod
    def _open_resource(cls, uri):
        """HACK - override _open_resource method to load resource files from the original PollBlock."""
        return (
            importlib.resources.files(
                inspect.getmodule(OverriddenPollBlock).__package__
            )
            .joinpath(cls.resources_dir)
            .joinpath(uri)
            .open("rb")
        )

    display_name = TranslatableString(default=_("Poll"))
    question = TranslatableString(default=_("What is your favorite color?"))
    answers = TranslatableList(
        default=[
            ("R", {"label": _("Red"), "img": None, "img_alt": None}),
            ("B", {"label": _("Blue"), "img": None, "img_alt": None}),
            ("G", {"label": _("Green"), "img": None, "img_alt": None}),
            ("O", {"label": _("Other"), "img": None, "img_alt": None}),
        ],
        scope=Scope.settings,
        help=_("The answer options on this poll."),
    )

    @XBlock.supports("multi_device")
    def student_view(self, context, **kwargs):
        return super().student_view(context, **kwargs)
