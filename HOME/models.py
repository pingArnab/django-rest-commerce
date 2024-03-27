import datetime
import uuid
from DRC.core.DRCCommonUtil import HASH
from django.db import models
from DRC.core.DRCCommonUtil import KEYGEN
from DRC.core.DRCConstant import DEFAULT
from django.contrib.auth.models import User as authUser
from django.utils import timezone


class Carousel(models.Model):
    def uploadPathCustomizer_Carousel(self, filename=None):
        return '___uploads/{folder_name}/{sub_folder_name}/{file_name}.{file_extension}'.format(
            folder_name='Home',
            sub_folder_name=self.__class__.__name__,
            file_name=KEYGEN.getRandom_StringDigit(20),
            file_extension=str(filename).split('.')[-1]
        )

    seq_no = models.IntegerField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=50)
    url = models.URLField()
    image = models.ImageField(upload_to=uploadPathCustomizer_Carousel)
    image_placeholder = models.CharField(max_length=50, null=True, blank=True, editable=False)

    # TO_BE_REMOVED
    # def get_image_thumbnail(self):
    #     return blurhash.encode(self.image, x_components=4, y_components=3)

    # TO_BE_REMOVED
    # def save(self, *args, **kwargs):
    #     self.image_placeholder = self.get_image_thumbnail()
    #     super(Carousel, self).save(*args, **kwargs)


class SubHeading(models.Model):
    def uploadPathCustomizer_SubHeading(self, filename=None):
        return '___uploads/{folder_name}/{sub_folder_name}/{file_name}.{file_extension}'.format(
            folder_name='Home',
            sub_folder_name=self.__class__.__name__,
            file_name=KEYGEN.getRandom_StringDigit(20),
            file_extension=str(filename).split('.')[-1]
        )

    seq_no = models.IntegerField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=50)
    url = models.URLField()
    image = models.ImageField(upload_to=uploadPathCustomizer_SubHeading)
    # TO_BE_REMOVED
    image_placeholder = models.CharField(max_length=50, null=True, blank=True, editable=False)

    # TO_BE_REMOVED
    # def get_image_thumbnail(self):
    #     return blurhash.encode(self.image, x_components=4, y_components=3)

    # TO_BE_REMOVED
    # def save(self, *args, **kwargs):
    #     self.image_placeholder = self.get_image_thumbnail()
    #     super(SubHeading, self).save(*args, **kwargs)


class OTP(models.Model):
    class TYPE:
        RESET_PASSWORD = 'RP'

        ALL = [
            ('UC', 'Uncategorized'),
            ('RP', 'Reset Password'),
        ]
    # temp password
    user = models.ForeignKey(authUser, on_delete=models.CASCADE)
    idp_key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    otp_hash = models.CharField(max_length=100, null=True, blank=True)
    otp_valid_upto = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=2, choices=TYPE.ALL, default='UC')

    class Meta:
        unique_together = ('user', 'type')

    @staticmethod
    def genOTP():
        otp = KEYGEN.getRandom_Digit(DEFAULT.NO_OF_OTP_DIGIT)
        hash_key = HASH.getHash(otp)
        return {
            'otp': otp,
            'hash': hash_key,
        }

    def validateOTP(self, otp):
        otp = otp.lower().strip()
        input_otp_hash = HASH.getHash(otp)
        if (not self.otp_valid_upto) or (self.otp_valid_upto < timezone.now()):
            return {
                'status': 400,
                'msg': 'OTP expired'
            }
        # print(self.otp_hash, input_otp_hash, self.otp_hash == input_otp_hash)
        if self.otp_hash == input_otp_hash:
            return {'status': 200, 'msg': 'OTP Validated'}
        return {
            'status': 400,
            'msg': 'Wrong OTP'
        }

    def set_validity(self, days=0, minutes=0, milliseconds=0, microseconds=0):
        self.otp_valid_upto = (
                datetime.datetime.now().astimezone() +
                datetime.timedelta(minutes=days) +
                datetime.timedelta(minutes=minutes) +
                datetime.timedelta(milliseconds=milliseconds) +
                datetime.timedelta(microseconds=microseconds)
        )
