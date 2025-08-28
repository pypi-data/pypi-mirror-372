"""
Name Affirmation signal handlers
"""

import logging

from openedx_events.learning.signals import (
    IDV_ATTEMPT_APPROVED,
    IDV_ATTEMPT_CREATED,
    IDV_ATTEMPT_DENIED,
    IDV_ATTEMPT_PENDING
)

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.signals import VERIFIED_NAME_APPROVED
from edx_name_affirmation.statuses import VerifiedNameStatus
from edx_name_affirmation.tasks import (
    delete_verified_name_task,
    idv_update_verified_name_task,
    proctoring_update_verified_name_task
)

User = get_user_model()

log = logging.getLogger(__name__)


@receiver(post_save, sender=VerifiedName)
def verified_name_approved(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Emit a signal when a verified name's status is updated to "approved".
    """
    if instance.status == VerifiedNameStatus.APPROVED:
        VERIFIED_NAME_APPROVED.send(
          sender='name_affirmation',
          user_id=instance.user.id,
          profile_name=instance.profile_name
        )


@receiver(IDV_ATTEMPT_APPROVED)
@receiver(IDV_ATTEMPT_CREATED)
@receiver(IDV_ATTEMPT_DENIED)
@receiver(IDV_ATTEMPT_PENDING)
def handle_idv_event(sender, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Trigger update to verified names based on open edX IDV events.
    """
    event_data = kwargs.get('idv_attempt')
    user = User.objects.get(id=event_data.user.id)

    # If the user has a pending name change, use that as the full name
    try:
        user_full_name = user.pending_name_change
    except AttributeError:
        user_full_name = event_data.user.pii.name

    status = None
    if signal == IDV_ATTEMPT_APPROVED:
        status = VerifiedNameStatus.APPROVED
    elif signal == IDV_ATTEMPT_CREATED:
        status = VerifiedNameStatus.PENDING
    elif signal == IDV_ATTEMPT_PENDING:
        status = VerifiedNameStatus.SUBMITTED
    elif signal == IDV_ATTEMPT_DENIED:
        status = VerifiedNameStatus.DENIED
    else:
        log.info(f'IDV_ATTEMPT {signal} signal not recognized')  # driven by receiver decorator so should never happen
        return

    log.info(f'IDV_ATTEMPT {status} signal triggering Celery task for user {user.id} '
             f'with name {event_data.name}')
    idv_update_verified_name_task.delay(
        event_data.attempt_id,
        user.id,
        status,
        event_data.name,
        user_full_name,
    )


def platform_verification_delete_handler(sender, instance, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Receiver for VerificationAttempt deletions
    """
    platform_verification_attempt_id = instance.id
    log.info(
        'VerifiedName: platform_verification_delete_handler triggering Celery task for '
        'platform_verification_attempt_id=%(platform_verification_attempt_id)s',
        {
            'platform_verification_attempt_id': platform_verification_attempt_id,
        }
    )
    delete_verified_name_task.delay(platform_verification_attempt_id, None)


def proctoring_attempt_handler(
    attempt_id,
    user_id,
    status,
    full_name,
    profile_name,
    is_practice_exam,
    is_proctored,
    backend_supports_onboarding,
    **kwargs
):
    """
    Receiver for proctored exam attempt updates.

    Args:
        attempt_id(int): ID associated with the proctored exam attempt
        user_id(int): ID associated with the proctored exam attempt's user
        status(str): status in proctoring language for the proctored exam attempt
        full_name(str): name to be used as verified name
        profile_name(str): user's current profile name
        is_practice_exam(boolean): if the exam attempt is for a practice exam
        is_proctored(boolean): if the exam attempt is for a proctored exam
        backend_supports_onboarding(boolean): if the exam attempt is for an exam with a backend that supports onboarding
    """

    # We only care about updates from onboarding exams, or from non-practice proctored exams with a backend that
    # does not support onboarding. This is because those two event types are guaranteed to contain verification events,
    # whereas timed exams and proctored exams with a backend that does support onboarding are not guaranteed
    is_onboarding_exam = is_practice_exam and is_proctored and backend_supports_onboarding
    reviewable_proctored_exam = is_proctored and not is_practice_exam and not backend_supports_onboarding
    if not (is_onboarding_exam or reviewable_proctored_exam):
        return

    trigger_status = VerifiedNameStatus.trigger_state_change_from_proctoring(status)

    # only trigger celery task if status is relevant to name affirmation
    if trigger_status:
        proctoring_update_verified_name_task.delay(
            attempt_id,
            user_id,
            trigger_status,
            full_name,
            profile_name,
        )
    else:
        log.info('VerifiedName: proctoring_attempt_handler will not trigger Celery task for user %(user_id)s '
                 'with profile_name %(profile_name)s because of status %(status)s',
                 {
                     'user_id': user_id,
                     'profile_name': profile_name,
                     'status': status,
                 }
                 )


def proctoring_delete_handler(sender, instance, signal, **kwargs):  # pylint: disable=unused-argument
    """
    Receiver for proctoring attempt deletions

    Args:
        attempt_id(int): ID associated with the proctoring attempt
    """
    proctoring_attempt_id = instance.id
    log.info(
        'VerifiedName: proctoring_delete_handler triggering Celery task for '
        'proctoring_attempt_id=%(proctoring_attempt_id)s',
        {
            'proctoring_attempt_id': proctoring_attempt_id,
        }
    )
    delete_verified_name_task.delay(None, proctoring_attempt_id)
