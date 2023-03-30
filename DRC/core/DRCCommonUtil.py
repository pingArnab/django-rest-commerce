import logging
import random
import secrets
import string
import uuid
import hashlib

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def checkUser(user):
    try:
        profile = user.userprofile
    except:
        return False
    else:
        return True


def checkSeller(user):
    try:
        profile = user.seller
    except:
        return False
    else:
        return True


class KEYGEN:
    @staticmethod
    def getRandom_String(length: int = 5):
        # printing letters
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def getRandom_Digit(length: int = 5):
        # printing letters
        letters = string.digits
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def getRandom_StringDigit(length: int = 5):
        # printing letters
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def get_secure_random_string(length):
        secure_str = ''.join((secrets.choice(
            string.ascii_letters
            + string.digits
            + string.punctuation
        ) for i in range(length)))
        return secure_str

    @staticmethod
    def getUUID():
        return uuid.uuid4()


class AccessLevel:
    USER = 1
    SELLER = 3
    STAFF = 5
    ADMIN = 9

    @staticmethod
    def checkAccess(user, allowed_access_level=-1, min_access_level=0, max_access_level=9):
        redirect_map = {
            0: 'HOME:home',
            1: 'HOME:home',
            3: 'SELLER:dashboard',
            5: None,
            9: '/admin',
        }

        if user.is_superuser:
            logger.debug('User <{}> Not Allowed'.format(user.username))
            return redirect(redirect_map[AccessLevel.ADMIN])

        user_group = user.groups.all()
        user_level = 0

        if user_group:
            user_level = int(user_group[0].name[0] if user_group else 0)
        else:
            if checkUser(user):
                user_level = AccessLevel.USER
            elif checkSeller(user):
                user_level = AccessLevel.SELLER

        if allowed_access_level > -1 and allowed_access_level != user_level:
            logger.debug('User <{}> Not Allowed'.format(user.username))
            raise Http404('User Not Authorise')

        if user_level < min_access_level:
            raise Http404('User Not Authorise')
            # return redirect(redirect_map[user_level])

        if user_level > max_access_level:
            logger.debug('User <{}> Not Allowed'.format(user.username))
            return redirect(redirect_map[user_level])

        logger.debug('user <{}> Allowed'.format(user.username))
        return None


class CTfiles:
    UPLOAD_PATH = '___uploads/'

    CATEGORY_PATH = UPLOAD_PATH + 'Category/'
    PRODUCT_PATH = UPLOAD_PATH + 'Product/'
    SELLER_PATH = UPLOAD_PATH + 'Seller/'
    USER_PATH = UPLOAD_PATH + 'UserProfile/'
    TEMP_PATH = UPLOAD_PATH + 'Temp/'

    @staticmethod
    def store(path, file_data):
        if path:
            path = path + '/'
        else:
            path = CTfiles.TEMP_PATH
        fileStorage = FileSystemStorage()
        file = fileStorage.save(path + KEYGEN.getRandom_StringDigit(20), file_data)
        return fileStorage.url(file).replace(settings.MEDIA_URL, '')

    @staticmethod
    def delete(name, path=''):
        if path:
            path = str(path).strip()
            if path:
                if path[-1] != '/':
                    path += '/'
                else:
                    path = ''
            else:
                path = ''
        else:
            path = ''
        logger.debug('CTfiles.delete() -> file requested to delete : ' + str(path + name))

        if '___uploads' in (path + name):
            try:
                fileStorage = FileSystemStorage()
                fileStorage.delete(name=path + name)
                logger.debug('CTfiles.delete() -> file delete : ' + str(path + name))
            except Exception as e:
                logger.exception('CTfiles.delete-> error for file<{}>'.format(path + name) + str(e))
        else:
            logger.debug('CTfiles.delete() -> file delete not allowed: ' + str(path + name))


# Mailer Client
def sendmail(mailData=None):
    """
        template = loader.get_template('mail-view/password-reset-mail-view.html')
        mailData = {
            'sender': 'ABC <no-reply@abc.com>',
            'to': [email, ],
            'subject': 'ABC | Password Reset',
            'msg': template.render({'name': Auth_User.objects.get(username=email).get_full_name(),
                                    'tempPass': tempPass.get('passWord')}),
        }
        sendmail(mailData=mailData)
    """
    if mailData is None:
        return {
            'status': 500,
            'error': {
                'msg': 'sendmail :: ' + 'Empty Mail Data',
            }
        }

    from_email = mailData.get('sender') if (type(mailData.get('sender')) is str) else None

    reply_to = mailData.get('reply-to') if (type(mailData.get('reply-to')) is list) else None
    cc = mailData.get('cc') if (type(mailData.get('cc')) is list) else None
    bcc = mailData.get('bcc') if (type(mailData.get('bcc')) is list) else None
    to = mailData.get('to') if (type(mailData.get('to')) is list) else None

    subject = mailData.get('subject') if (type(mailData.get('subject')) is str) else ''
    message = mailData.get('msg')

    try:
        msg = EmailMultiAlternatives(subject=subject, body=message, from_email=from_email, to=to, cc=cc, bcc=bcc,
                                     reply_to=reply_to)
        msg.attach_alternative(message, "text/html")
        res = msg.send()

        if res == 1:
            return {
                'status': 200,
            }
    except Exception as e:
        print("mail exp: ", e)
        return {
            'status': 500,
            'error': {
                'msg': 'sendmail :: ' + 'Mail Client Error!',
                'desc': e,
            }
        }


class HASH:
    @staticmethod
    def getHash(data):
        private_key = bytes(data, 'utf-8')
        public_key = bytes('s#jh878!@8', 'utf-8')

        dk = hashlib.pbkdf2_hmac('sha256', private_key, public_key, 100000)
        return dk.hex()


class MONTH:
    MONTH_LIST = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    MONTH_SHORT_LIST = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    @staticmethod
    def get_name(month_num):
        return MONTH.MONTH_LIST[month_num]

    @staticmethod
    def get_short_name(month_num):
        return MONTH.MONTH_SHORT_LIST[month_num]
