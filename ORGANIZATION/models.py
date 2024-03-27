import uuid

from nanoid import generate as nanoid_generate
from django.db import models
from django.contrib.auth.models import User as AuthUser


# Create your models here.
def generate_org_id():
    return f'ORG_{nanoid_generate()}'


def generate_logo_file_path(self, filename=None):
    return '{folder_name}/{sub_folder_name}/{file_name}.{file_extension}'.format(
        folder_name=self.__class__.__name__,
        sub_folder_name=self.id,
        file_name=nanoid_generate(),
        file_extension=str(filename).split('.')[-1]
    )


class Organization(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=25, default=generate_org_id)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    logo = models.ImageField(upload_to=generate_logo_file_path, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    owner = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='owner')
    staff = models.ManyToManyField(AuthUser, through='Permission', related_name='staff')

    def __str__(self):
        return f'{self.name}'


class Permission(models.Model):
    class PRODUCT_PERMISSION:
        NO_PERMISSION = 0
        VIEW_PERMISSION = 1
        VIEW_EDIT_PERMISSION = 2
        ALL_PERMISSION = 3
        __CHOICES_LIST = [
            (0, "NO_PERMISSION"),
            (1, "VIEW_PERMISSION"),
            (2, "VIEW_EDIT_PERMISSION"),
            (3, "ALL_PERMISSION"),
        ]

        def get_all_choice_list(self):
            return self.__CHOICES_LIST

    class ORDER_PERMISSION:
        NO_PERMISSION = 0
        VIEW_PERMISSION = 1
        EXECUTE_PERMISSION = 2
        EXECUTE_OR_REJECT_PERMISSION = 3
        __CHOICES_LIST = [
            (0, "NO_PERMISSION"),
            (1, "VIEW_PERMISSION"),
            (2, "EXECUTE_PERMISSION"),
            (3, "EXECUTE_OR_REJECT_PERMISSION"),
        ]

        def get_all_choice_list(self):
            return self.__CHOICES_LIST

    class ROLE:
        VIEWER = 1
        EDITOR = 2
        ADMIN = 3
        __CHOICE_LIST = [
            (1, "VIEWER"),
            (2, "EDITOR"),
            (3, "ADMIN"),
        ]

        def get_all_role_list(self):
            return self.__CHOICE_LIST

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE().get_all_role_list())
    product = models.PositiveSmallIntegerField(choices=PRODUCT_PERMISSION().get_all_choice_list())
    order = models.PositiveSmallIntegerField(choices=ORDER_PERMISSION().get_all_choice_list())

    class Meta:
        unique_together = ('staff', 'organization')

    def __str__(self):
        return f'{self.staff.username}-{self.organization.name}'
