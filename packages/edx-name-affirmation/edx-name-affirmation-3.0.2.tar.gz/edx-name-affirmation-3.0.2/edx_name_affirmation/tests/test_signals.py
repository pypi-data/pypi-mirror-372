"""
Tests for Name Affirmation signals
"""

import ddt

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.signals import _listen_for_lms_retire_verified_names

User = get_user_model()


@ddt.ddt
class RetirementSignalVerifiedNamesTest(TestCase):
    """
    Tests for the LMS User Retirement signal for Verified Names
    """

    def setUp(self):
        self.user = User(username='tester', email='tester@test.com')
        self.user.save()
        self.name = 'Jonathan Smith'
        self.profile_name = 'Jon Smith'
        self.idv_attempt_id = 1111111
        self.verified_name_obj = VerifiedName.objects.create(
            user=self.user,
            verified_name=self.name,
            profile_name=self.profile_name,
            verification_attempt_id=self.idv_attempt_id
        )

        self.other_user = User(username='other_tester', email='other_tester@test.com')
        self.other_user.save()
        self.other_name = 'Jonathan Other'
        self.other_profile_name = 'Jon Other'
        self.other_idv_attempt_id = 1111112
        self.verified_name_obj = VerifiedName.objects.create(
            user=self.other_user,
            verified_name=self.other_name,
            profile_name=self.other_profile_name,
            verification_attempt_id=self.other_idv_attempt_id
        )

    def test_retirement_signal(self):
        _listen_for_lms_retire_verified_names(sender=self.__class__, user=self.user)
        self.assertEqual(len(VerifiedName.objects.filter(user=self.user)), 0)
        self.assertEqual(len(VerifiedName.objects.filter(user=self.other_user)), 1)

    def test_retirement_signal_no_verified_names(self):
        no_verified_user = User(username='no_verified', email='no_verified@test.com')
        _listen_for_lms_retire_verified_names(sender=self.__class__, user=no_verified_user)
        self.assertEqual(len(VerifiedName.objects.all()), 2)

    def test_retirement_signal_all_verified_names_for_user(self):
        # create a second verified name for user to check that both names are deleted
        VerifiedName.objects.create(
            user=self.user,
            verified_name='J Smith',
            profile_name=self.profile_name,
            verification_attempt_id=1111112
        )
        _listen_for_lms_retire_verified_names(sender=self.__class__, user=self.user)
        self.assertEqual(len(VerifiedName.objects.filter(user=self.user)), 0)
