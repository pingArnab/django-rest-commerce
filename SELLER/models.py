import logging
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User as authUser
from DRC.core.DRCCommonUtil import KEYGEN
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def generateCategoryId():
    start = datetime.now().microsecond
    seller_id = 'SEL_' + KEYGEN.getRandom_Digit(12)
    while Seller.objects.filter(seller_id=seller_id):
        logger.error(':: generateCategoryId: duplicate Category Id: {}'.format(seller_id))
        seller_id = 'SEL_' + KEYGEN.getRandom_StringDigit(12)
    end = datetime.now().microsecond
    logger.error('generateCategoryId -> ' + str(end - start) + 'micros')
    return seller_id


# Create your models here.
class Seller(models.Model):

    # image Upload Path Customizer
    def uploadPathCustomizer(self, filename=None):
        return '___uploads/{folder_name}/{sub_folder_name}/{file_name}.{file_extension}/'.format(
            folder_name=self.__class__.__name__,
            sub_folder_name=self.user.username,
            file_name=KEYGEN.getRandom_StringDigit(20),
            file_extension=str(filename).split('.')[-1]
        )

    user = models.OneToOneField(authUser, on_delete=models.CASCADE)
    seller_id = models.SlugField(max_length=16, default=generateCategoryId, auto_created=True, unique=True,
                                 blank=False, null=False, editable=False)
    # name = models.CharField(max_length=100, blank=False, null=False)
    # email = models.EmailField(null=True, blank=True)
    ph_no = models.CharField(max_length=20, blank=False, null=False)
    alt_ph_no = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to=uploadPathCustomizer, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    gstin = models.CharField(max_length=25, unique=True, null=True, blank=True)

    features = models.TextField(default={}, editable=False)
    total_sale = models.IntegerField(default=0, editable=False)

    verified = models.BooleanField(default=False)

    def get_full_name(self):
        return '{}'.format(self.user.get_full_name())

    def __str__(self):
        return '{}'.format(self.user.username)
