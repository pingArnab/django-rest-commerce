from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from django.template import loader
from DRC.core.exceptions import ErrorResponse
from DRC.settings import CONFIG
from DRC.settings import D


class Mail:
    def __init__(self, sender, subject, body, reply_to, to, cc=None, bcc=None):
        self.sender = sender
        self.reply_to = reply_to
        self.cc = cc
        self.bcc = bcc
        self.to = to
        self.subject = subject
        self.body = body

    def check_error(self):
        if not (self.sender and type(self.sender) is str):
            print('Field error:', 'sender => ', self.sender)
            return ErrorResponse(code=400, msg='from_email is Invalid').response
        if not (self.reply_to and type(self.reply_to) is list):
            print('Field error:', 'reply_to => ', self.reply_to)
            return ErrorResponse(code=400, msg='reply_to is mandatory and must be a string').response
        if self.cc and not (type(self.cc) is list):
            print('Field error:', 'cc => ', self.cc)
            return ErrorResponse(code=400, msg='cc must be a list').response
        if self.bcc and not (type(self.bcc) is list):
            print('Field error:', 'bcc => ', self.bcc)
            return ErrorResponse(code=400, msg='bcc must be a list').response
        if not (self.to and type(self.to) is list):
            print('Field error:', 'to => ', self.to)
            return ErrorResponse(code=400, msg='to is mandatory and must be a list').response
        if self.subject and not (type(self.subject) is str):
            print('Field error:', 'subject => ', self.subject)
            return ErrorResponse(code=400, msg='subject must be a string').response
        # if self.body and not (type(self.body) is str):
        #     print('Field error:', 'message => ', self.body)
        #     return ErrorResponse(code=400, msg='message must be a string').response

    def send(self):
        error = self.check_error()
        if error:
            return error

        try:
            msg = EmailMultiAlternatives(
                subject=self.subject,
                body=self.bcc,
                from_email=self.sender,
                to=self.to,
                cc=self.cc,
                bcc=self.bcc,
                reply_to=self.reply_to
            )
            msg.attach_alternative(self.body, "text/html")
            res = msg.send()

            if res == 1:
                return Response({'status': 'Success', 'msg': 'A verification mail has been sent to your mail'})
        except Exception as ex:
            return ErrorResponse(
                code=500,
                msg='Error in sending mail',
                details=ex.__str__()
            ).response


class UserVerificationMail(Mail):
    def __init__(self, receiver, name, url):
        self.body_template = loader.get_template('mail/verify_user.html')
        self.name = name
        self.url = url
        super().__init__(
            sender=f'{CONFIG.MAIL.NAME} <{CONFIG.MAIL.ADDRESS}>',
            to=[receiver, ],
            reply_to=CONFIG.MAIL.REPLY_TO,
            subject=f'{CONFIG.PROJECT_NAME} | Account Verification',
            body=self.body_template.render({'name': self.name, 'url': self.url})
        )


class PasswordResetMail(Mail):
    def __init__(self, receiver, name, otp):
        self.body_template = loader.get_template('mail/reset_password.html')
        self.name = name
        self.otp = otp
        super().__init__(
            sender=f'{CONFIG.MAIL.NAME} <{CONFIG.MAIL.ADDRESS}>',
            to=[receiver, ],
            reply_to=CONFIG.MAIL.REPLY_TO,
            subject=f'{CONFIG.PROJECT_NAME} | Password Reset',
            body=self.body_template.render({'name': self.name, 'otp': self.otp})
        )
