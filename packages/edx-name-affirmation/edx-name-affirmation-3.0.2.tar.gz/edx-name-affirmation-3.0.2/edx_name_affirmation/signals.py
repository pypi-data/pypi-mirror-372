"""
Name Affirmation signals
"""

from django.dispatch import Signal
from django.dispatch.dispatcher import receiver

try:
    from openedx.core.djangoapps.user_api.accounts.signals import USER_RETIRE_LMS_MISC
except ImportError:
    # An ImportError should only be raised in tests, where the code is not running as an installation of
    # edx-platform. In this case, the import should default to a generic Signal.
    USER_RETIRE_LMS_MISC = Signal()

from .models import VerifiedName

VERIFIED_NAME_APPROVED = Signal()


@receiver(USER_RETIRE_LMS_MISC)
def _listen_for_lms_retire_verified_names(sender, **kwargs):  # pylint: disable=unused-argument
    user = kwargs.get('user')
    VerifiedName.retire_user(user.id)
