"""
Database models for edx_name_affirmation.
"""

from config_models.models import ConfigurationModel
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from edx_name_affirmation.statuses import VerifiedNameStatus

try:
    from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
    from lms.djangoapps.verify_student.models import VerificationAttempt as PlatformVerificationAttempt
except ImportError:
    SoftwareSecurePhotoVerification = None
    PlatformVerificationAttempt = None

User = get_user_model()


class VerifiedName(TimeStampedModel):
    """
    This model represents a verified name for a user, with a link to the source
    through `verification_attempt_id` or `proctored_exam_attempt_id` if applicable.

    .. pii: Contains name fields.
    .. pii_types: name
    .. pii_retirement: local_api
    """
    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    verified_name = models.CharField(max_length=255, db_index=True)

    # Snapshot of the user's UserProfile `name` upon creation
    profile_name = models.CharField(max_length=255, null=True)

    # Reference to an external ID verification or proctored exam attempt
    verification_attempt_id = models.PositiveIntegerField(null=True, blank=True)
    proctored_exam_attempt_id = models.PositiveIntegerField(null=True, blank=True)

    # Reference to a generic VerificationAttempt object in the platform
    platform_verification_attempt_id = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=32,
        choices=[(st.value, st.value) for st in VerifiedNameStatus],
        default=VerifiedNameStatus.PENDING.value,
    )
    history = HistoricalRecords()

    @classmethod
    def retire_user(cls, user_id):
        """
        Retire user as part of GDPR pipeline
        :param user_id: int
        """
        verified_names = cls.objects.filter(user_id=user_id)
        verified_names.delete()

    class Meta:
        """ Meta class for this Django model """
        db_table = 'nameaffirmation_verifiedname'
        verbose_name = 'verified name'

    @property
    def verification_attempt_status(self):
        "Returns the status associated with its SoftwareSecurePhotoVerification with verification_attempt_id if any."

        if not self.verification_attempt_id or not SoftwareSecurePhotoVerification:
            return None

        try:
            verification = SoftwareSecurePhotoVerification.objects.get(id=self.verification_attempt_id)
            return verification.status

        except ObjectDoesNotExist:
            return None

    @property
    def platform_verification_attempt_status(self):
        """
        Returns the status associated with its platform VerificationAttempt
        """
        if not self.platform_verification_attempt_id or not PlatformVerificationAttempt:
            return None

        try:
            verification = PlatformVerificationAttempt.objects.get(id=self.platform_verification_attempt_id)
            return verification.status

        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """
        Validate only one of `verification_attempt_id` or `platform_verification_attempt_id`
        can be set.
        """
        if self.verification_attempt_id and self.platform_verification_attempt_id:
            raise ValueError('Only one of `verification_attempt_id` or `platform_verification_attempt_id` can be set.')
        super().save(*args, **kwargs)


class VerifiedNameConfig(ConfigurationModel):
    """
    This model provides various configuration fields for users regarding their
    verified name.
    .. no_pii: This model has no PII.
    """
    KEY_FIELDS = ('user',)

    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE, related_name='verified_name_config')
    use_verified_name_for_certs = models.BooleanField(default=False)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'nameaffirmation_verifiednameconfig'
        verbose_name = 'verified name config'
