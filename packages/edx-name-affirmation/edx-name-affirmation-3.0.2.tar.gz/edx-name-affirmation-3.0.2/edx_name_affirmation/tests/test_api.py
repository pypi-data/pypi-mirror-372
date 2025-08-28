"""
Tests for the `edx_name_affirmation` Python API.
"""

import ddt

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from edx_name_affirmation.api import (
    create_verified_name,
    create_verified_name_config,
    get_verified_name,
    get_verified_name_history,
    should_use_verified_name_for_certs,
    update_verified_name_status
)
from edx_name_affirmation.exceptions import (
    VerifiedNameAttemptIdNotGiven,
    VerifiedNameDoesNotExist,
    VerifiedNameEmptyString,
    VerifiedNameMultipleAttemptIds
)
from edx_name_affirmation.models import VerifiedNameConfig
from edx_name_affirmation.statuses import VerifiedNameStatus

User = get_user_model()


@ddt.ddt
class TestVerifiedNameAPI(TestCase):
    """
    Tests for the VerifiedName API.
    """
    VERIFIED_NAME = 'Jonathan Doe'
    PROFILE_NAME = 'Jon Doe'
    VERIFICATION_ATTEMPT_ID = 123
    PROCTORED_EXAM_ATTEMPT_ID = 456
    PLATFORM_VERIFICATION_ATTEMPT_ID = 789

    def setUp(self):
        super().setUp()
        self.user = User(username='jondoe', email='jondoe@test.com')
        self.user.save()
        # Create a fresh config with default values
        VerifiedNameConfig.objects.create(user=self.user)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_create_verified_name_defaults(self):
        """
        Test to create a verified name with default values.
        """
        verified_name_obj = self._create_verified_name()

        self.assertEqual(verified_name_obj.user, self.user)
        self.assertIsNone(verified_name_obj.verification_attempt_id)
        self.assertIsNone(verified_name_obj.proctored_exam_attempt_id)
        self.assertEqual(verified_name_obj.status, VerifiedNameStatus.PENDING.value)

    @ddt.data(
        (123, None, None, VerifiedNameStatus.APPROVED),
        (None, 456, None, VerifiedNameStatus.SUBMITTED),
        (None, None, 789, VerifiedNameStatus.SUBMITTED),
    )
    @ddt.unpack
    def test_create_verified_name_with_optional_arguments(
        self, verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id, status,
    ):
        """
        Test to create a verified name with optional arguments supplied.
        """
        verified_name_obj = self._create_verified_name(
            verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id, status,
        )

        self.assertEqual(verified_name_obj.verification_attempt_id, verification_attempt_id)
        self.assertEqual(verified_name_obj.proctored_exam_attempt_id, proctored_exam_attempt_id)
        self.assertEqual(verified_name_obj.platform_verification_attempt_id, platform_verification_attempt_id)
        self.assertEqual(verified_name_obj.status, status.value)

    @ddt.data(
        (123, 456, None),
        (123, None, 789),
        (None, 456, 789),
        (123, 456, 789),
    )
    @ddt.unpack
    def test_create_verified_name_two_ids(
        self, verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id
    ):
        """
        Test that a verified name cannot be created with both a verification_attempt_id
        and a proctored_exam_attempt_id.
        """
        with self.assertRaises(VerifiedNameMultipleAttemptIds):
            create_verified_name(
                self.user,
                self.VERIFIED_NAME,
                self.PROFILE_NAME,
                verification_attempt_id,
                proctored_exam_attempt_id,
                platform_verification_attempt_id,
            )

    @ddt.data(
        ('', PROFILE_NAME),
        (VERIFIED_NAME, ''),
    )
    @ddt.unpack
    def test_create_verified_name_empty_string(self, verified_name, profile_name):
        """
        Test that an empty verified_name or profile_name will raise an exception.
        """
        field = ''
        if verified_name == '':
            field = 'verified_name'
        elif profile_name == '':
            field = 'profile_name'

        with self.assertRaises(VerifiedNameEmptyString) as context:
            create_verified_name(self.user, verified_name, profile_name)

        self.assertEqual(
            str(context.exception),
            'Attempted to create VerifiedName for user_id={user_id}, but {field} was '
            'empty.'.format(field=field, user_id=self.user.id),
        )

    def test_get_verified_name_most_recent(self):
        """
        Test to get the most recent verified name.
        """
        create_verified_name(self.user, 'old verified name', 'old profile name')
        self._create_verified_name()

        verified_name_obj = get_verified_name(self.user)

        self.assertEqual(verified_name_obj.verified_name, self.VERIFIED_NAME)
        self.assertEqual(verified_name_obj.profile_name, self.PROFILE_NAME)

    def test_get_verified_name_only_verified(self):
        """
        Test that VerifiedName entries with status != approved are ignored if is_verified
        argument is set to True.
        """
        self._create_verified_name(status=VerifiedNameStatus.APPROVED)
        create_verified_name(self.user, 'unverified name', 'unverified profile name')

        verified_name_obj = get_verified_name(self.user, True)

        self.assertEqual(verified_name_obj.verified_name, self.VERIFIED_NAME)
        self.assertEqual(verified_name_obj.profile_name, self.PROFILE_NAME)

    @ddt.data(False, True)
    def test_get_verified_name_none_exist(self, check_is_verified):
        """
        Test that None returns if there are no VerifiedName entries. If the `is_verified`
        flag is set to True, and there are only non-verified entries, we should get the
        same result.
        """
        if check_is_verified:
            self._create_verified_name()
            verified_name_obj = get_verified_name(self.user, True)
        else:
            verified_name_obj = get_verified_name(self.user)

        self.assertIsNone(verified_name_obj)

    @ddt.data(
        ([VerifiedNameStatus.PENDING], VerifiedNameStatus.DENIED),
        ([VerifiedNameStatus.DENIED, VerifiedNameStatus.PENDING], VerifiedNameStatus.APPROVED),
        (['invalid status'], VerifiedNameStatus.PENDING)
    )
    @ddt.unpack
    def test_get_verified_name_exclude(self, statuses_to_exclude, expected_status):
        """
        Exclude verified names by status when getting the most recent verified name.
        """
        self._create_verified_name(status=VerifiedNameStatus.APPROVED)
        self._create_verified_name(status=VerifiedNameStatus.DENIED)
        self._create_verified_name(status=VerifiedNameStatus.PENDING)

        verified_name_obj = get_verified_name(self.user, False, statuses_to_exclude)

        self.assertEqual(verified_name_obj.status, expected_status)

    @ddt.data(False, True)
    def test_get_verified_name_ignore_exlude_parameter(self, is_verified):
        """
        If `is_verified` is True, ignore the `statuses_to_exclude` parameter.
        """
        self._create_verified_name(status=VerifiedNameStatus.APPROVED)

        verified_name_obj = get_verified_name(self.user, is_verified, [VerifiedNameStatus.APPROVED])

        if is_verified:
            self.assertEqual(verified_name_obj.verified_name, self.VERIFIED_NAME)
        else:
            self.assertIsNone(verified_name_obj)

    def test_get_verified_name_history(self):
        """
        Test that get_verified_name_history returns all of the user's VerifiedNames
        ordered by most recently created.
        """
        verified_name_first = self._create_verified_name()
        verified_name_second = self._create_verified_name()

        verified_name_qs = get_verified_name_history(self.user)
        self.assertEqual(verified_name_qs[1].id, verified_name_first.id)
        self.assertEqual(verified_name_qs[0].id, verified_name_second.id)

    @ddt.data(
        (VERIFICATION_ATTEMPT_ID, None, None),
        (None, PROCTORED_EXAM_ATTEMPT_ID, None),
        (None, None, PLATFORM_VERIFICATION_ATTEMPT_ID)
    )
    @ddt.unpack
    def test_update_is_verified_status(
        self, verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id,
    ):
        """
        Test that VerifiedName status can be updated with a given attempt ID.
        """
        self._create_verified_name(verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id)
        update_verified_name_status(
            self.user,
            VerifiedNameStatus.DENIED,
            verification_attempt_id,
            proctored_exam_attempt_id,
            platform_verification_attempt_id,
        )
        verified_name_obj = get_verified_name(self.user)
        self.assertEqual(VerifiedNameStatus.DENIED.value, verified_name_obj.status)

    def test_update_is_verified_no_attempt_id(self):
        """
        Test that `update_is_verified_by_attempt_id` will raise an exception with no attempt
        ID given.
        """
        with self.assertRaises(VerifiedNameAttemptIdNotGiven):
            update_verified_name_status(self.user, True)

    @ddt.data(
        (123, 456, None),
        (123, None, 789),
        (None, 456, 789),
        (123, 456, 789),
    )
    @ddt.unpack
    def test_update_is_verified_multiple_attempt_ids(
        self, verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id
    ):
        """
        Test that `update_is_verified_by_attempt_id` will raise an exception with multiple attempt
        IDs given.
        """
        with self.assertRaises(VerifiedNameMultipleAttemptIds):
            update_verified_name_status(
                self.user, True, verification_attempt_id, proctored_exam_attempt_id, platform_verification_attempt_id,
            )

    def test_update_is_verified_does_not_exist(self):
        """
        Test that `update_is_verified_by_attempt_id` will raise an exception if a VerifiedName does
        not exist for the attempt ID given.
        """
        with self.assertRaises(VerifiedNameDoesNotExist):
            update_verified_name_status(self.user, True, self.VERIFICATION_ATTEMPT_ID)

    def _create_verified_name(
        self, verification_attempt_id=None, proctored_exam_attempt_id=None,
        platform_verification_attempt_id=None, status=VerifiedNameStatus.PENDING,
    ):
        """
        Util to create and return a VerifiedName with default names.
        """
        create_verified_name(
            self.user, self.VERIFIED_NAME, self.PROFILE_NAME, verification_attempt_id,
            proctored_exam_attempt_id, platform_verification_attempt_id, status
        )
        return get_verified_name(self.user)

    @ddt.data(
        (True, True),
        (True, False),
        (False, False),
    )
    @ddt.unpack
    def test_should_use_verified_name_for_certs(self, create_config, expected_value):
        """
        Test that the correct config value is returned from `should_use_verified_name_for_certs`
        """
        if create_config:
            VerifiedNameConfig.objects.create(user=self.user, use_verified_name_for_certs=expected_value)

        # create config for other user, make sure it is the opposite of the expected value.
        # we want to add an additional config to make sure that caching by user works properly
        other_user = User(username='bobsmith', email='bobsmith@test.com')
        other_user.save()
        VerifiedNameConfig.objects.create(user=other_user, use_verified_name_for_certs=not expected_value)

        should_use_for_certs = should_use_verified_name_for_certs(self.user)
        self.assertEqual(should_use_for_certs, expected_value)

    def test_create_verified_name_config(self):
        """
        Test that verified name config is created and updated successfully
        """
        create_verified_name_config(self.user, use_verified_name_for_certs=True)

        # check that new record was created
        config_obj = VerifiedNameConfig.current(self.user)
        self.assertTrue(config_obj.use_verified_name_for_certs)
        self.assertEqual(config_obj.user, self.user)

    def test_create_verified_name_config_no_overwrite(self):
        """
        Test that if a field is set to True, it will not be overridden by False
        if not specified when the config is updated
        """
        create_verified_name_config(self.user, use_verified_name_for_certs=True)
        create_verified_name_config(self.user)
        self.assertTrue(should_use_verified_name_for_certs(self.user))
