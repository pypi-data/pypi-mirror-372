# pylint: disable=logging-format-interpolation, unused-argument
"""
Name affirmation celery tasks
"""

import logging

from celery import shared_task
from edx_django_utils.monitoring import set_code_owner_attribute

from django.contrib.auth import get_user_model
from django.db.models import Q

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus

User = get_user_model()

log = logging.getLogger(__name__)

DEFAULT_RETRY_SECONDS = 30
MAX_RETRIES = 3


@shared_task(
    bind=True, autoretry_for=(Exception,), default_retry_delay=DEFAULT_RETRY_SECONDS, max_retries=MAX_RETRIES,
)
@set_code_owner_attribute
def idv_update_verified_name_task(self, attempt_id, user_id, name_affirmation_status, photo_id_name, full_name):
    """
    Celery task for updating a verified name based on an IDV attempt
    """
    log.info('VerifiedName: idv_update_verified_name triggering Celery task started for user %(user_id)s '
             'with attempt_id %(attempt_id)s and status %(status)s',
             {
                'user_id': user_id,
                'attempt_id': attempt_id,
                'status': name_affirmation_status
             }
             )
    # get all verified names that are either not associated with an IDV attempt, or
    # only associated with the IDV attempt for which we received an update. We do not
    # want to grab all verified names for the same user and name combination, because
    # some of those records may already be associated with a different IDV attempt.
    verified_names = VerifiedName.objects.filter(
        (Q(platform_verification_attempt_id=attempt_id) | Q(platform_verification_attempt_id__isnull=True))
        & Q(user__id=user_id)
        & Q(verified_name=photo_id_name)
    ).order_by('-created')
    verified_names_updated = False
    if verified_names:
        # if there are VerifiedName objects, we want to update existing entries
        # for each attempt with no attempt id (either proctoring or idv), update attempt id
        updated_for_attempt_id = verified_names.filter(
            proctored_exam_attempt_id=None,
            verification_attempt_id=None,
            platform_verification_attempt_id=None
        ).update(platform_verification_attempt_id=attempt_id)

        if updated_for_attempt_id:
            verified_names_updated = True
            log.info(
                'Updated VerifiedNames for user={user_id} to platform_verification_attempt_id={attempt_id}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                )
            )

        # then for all matching attempt ids, update the status
        verified_name_qs = verified_names.filter(
            platform_verification_attempt_id=attempt_id,
            verification_attempt_id=None,
            proctored_exam_attempt_id=None
        )

        # Individually update to ensure that post_save signals send
        for verified_name_obj in verified_name_qs:
            verified_name_obj.status = name_affirmation_status
            verified_name_obj.save()
            verified_names_updated = True

        log.info(
            'Updated VerifiedNames for user={user_id} with platform_verification_attempt_id={attempt_id} to '
            'have status={status}'.format(
                user_id=user_id,
                attempt_id=attempt_id,
                status=name_affirmation_status
            )
        )

    # if there are no entries to update, we want to create one.
    if not verified_names_updated:
        user = User.objects.get(id=user_id)
        verified_name = VerifiedName.objects.create(
            user=user,
            verified_name=photo_id_name,
            profile_name=full_name,
            platform_verification_attempt_id=attempt_id,
            status=name_affirmation_status,
        )
        log.error(
            'Created VerifiedName for user={user_id} to have status={status} '
            'and platform_verification_attempt_id={attempt_id}, because no matching '
            'attempt_id or verified_name were found.'.format(
                user_id=user_id,
                attempt_id=attempt_id,
                status=verified_name.status
            )
        )


@shared_task(
    bind=True, autoretry_for=(Exception,), default_retry_delay=DEFAULT_RETRY_SECONDS, max_retries=MAX_RETRIES,
)
@set_code_owner_attribute
def proctoring_update_verified_name_task(
    self,
    attempt_id,
    user_id,
    name_affirmation_status,
    full_name,
    profile_name
):
    """
    Celery task for updating a verified name based on a proctoring attempt
    """

    approved_verified_name = VerifiedName.objects.filter(
        user__id=user_id,
        status=VerifiedNameStatus.APPROVED
    ).order_by('-created').first()

    verified_name_for_exam = VerifiedName.objects.filter(
        user__id=user_id,
        proctored_exam_attempt_id=attempt_id
    ).order_by('-created').first()

    # check if approved VerifiedName already exists for the user, and skip
    # update if no VerifiedName has already been created for this specific exam
    if approved_verified_name and not verified_name_for_exam:
        is_full_name_approved = approved_verified_name.verified_name == full_name
        if not is_full_name_approved:
            log.warning(
                'Full name for proctored_exam_attempt_id={attempt_id} is not equal '
                'to the most recent verified name verified_name_id={name_id}.'.format(
                    attempt_id=attempt_id,
                    name_id=approved_verified_name.id
                )
            )
        return

    if verified_name_for_exam:
        verified_name_for_exam.status = name_affirmation_status
        verified_name_for_exam.save()
        log.info(
            'Updated VerifiedName for user={user_id} with proctored_exam_attempt_id={attempt_id} '
            'to have status={status}'.format(
                user_id=user_id,
                attempt_id=attempt_id,
                status=name_affirmation_status
            )
        )
    else:
        if full_name and profile_name:
            # if they do not already have an approved VerifiedName, create one
            user = User.objects.get(id=user_id)
            VerifiedName.objects.create(
                user=user,
                verified_name=full_name,
                proctored_exam_attempt_id=attempt_id,
                status=name_affirmation_status,
                profile_name=profile_name
            )
            log.info(
                'Created VerifiedName for user={user_id} to have status={status} '
                'and proctored_exam_attempt_id={attempt_id}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                    status=name_affirmation_status
                )
            )
        else:
            log.error(
                'Cannot create VerifiedName for user={user_id} for proctored_exam_attempt_id={attempt_id} '
                'because neither profile name nor full name were provided'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                )
            )


@shared_task(
    bind=True, autoretry_for=(Exception,), default_retry_delay=DEFAULT_RETRY_SECONDS, max_retries=MAX_RETRIES,
)
@set_code_owner_attribute
def delete_verified_name_task(self, platform_verification_attempt_id, proctoring_attempt_id):
    """
    Celery task to delete a verified name based on an idv or proctoring attempt
    """
    # this case shouldn't happen, but should log as an error in case
    if (proctoring_attempt_id, platform_verification_attempt_id).count(None) != 1:
        log.error(
            'A maximum of one attempt id should be provided'
        )
        return

    log_message = {'field_name': '', 'attempt_id': ''}

    if platform_verification_attempt_id:
        verified_names = VerifiedName.objects.filter(platform_verification_attempt_id=platform_verification_attempt_id)
        log_message['field_name'] = 'platform_verification_attempt_id'
        log_message['attempt_id'] = platform_verification_attempt_id
    else:
        verified_names = VerifiedName.objects.filter(proctored_exam_attempt_id=proctoring_attempt_id)
        log_message['field_name'] = 'proctored_exam_attempt_id'
        log_message['attempt_id'] = proctoring_attempt_id

    if verified_names:
        log.info(
            'Deleting {num_names} VerifiedName(s) associated with {field_name}='
            '{platform_verification_attempt_id}'.format(
                num_names=len(verified_names),
                field_name=log_message['field_name'],
                platform_verification_attempt_id=log_message['attempt_id'],
            )
        )
        verified_names.delete()

    log.info(
        'No VerifiedNames deleted because no VerifiedNames were associated with the provided attempt ID.'
    )
