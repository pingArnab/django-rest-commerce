import json
import logging
import traceback

from django.contrib import messages
from django.template import loader
from django.contrib.auth.models import User as authUser
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from datetime import datetime, timedelta
from django.utils import timezone

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User as AuthUser
from HOME.models import OTP
from SELLER.models import Seller
from USER import utils as user_utils
from django.contrib.auth.models import User
from DRC.core.DRCCommonUtil import AccessLevel, sendmail
from DRC.core.DRCConstant import DEFAULT
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def get_home(request):
    if not request.user.is_authenticated:
        return redirect('HOME:login')
    if request.user.is_superuser or request.user.is_staff:
        return redirect(reverse('admin:index'))
    elif Seller.objects.filter(user__username=request.user.username):
        return redirect('SELLER:dashboard')
    else:
        messages.error(request, 'This user is not Seller / Staff')
        raise Http404


def login(request):
    if request.user.is_authenticated:
        messages.error(request, 'Already logged in')
        return redirect('HOME:home')
    if request.method == 'POST':
        try:
            auth_user: AuthUser = AuthUser.objects.get(username=request.POST.get('username'))
            if auth_user and (
                    auth_user.is_superuser or
                    auth_user.is_staff or
                    Seller.objects.filter(user_id=auth_user.id)
            ):
                authenticated_user = authenticate(request, username=request.POST.get('username'),
                                                  password=request.POST.get('password'))
                if authenticated_user is not None:
                    auth_login(request, authenticated_user)
                    return redirect('HOME:home')
                else:
                    messages.error(request, 'Incorrect password, please try again')
            else:
                messages.error(request, 'No seller / staff found with this email')
        except Exception as ex:
            messages.error(request, 'no Seller / Staff found with this email')
    return render(request, 'USER/login-page.html')


def logout(request):
    auth_logout(request)
    return redirect('HOME:login')


@csrf_exempt
def forgetPassword(request):
    context = {}
    if request.user.is_authenticated:
        logger.debug('forgetPassword =>user already authenticated: {}'.format(request.user.username))
        raise Http404

    if request.method == 'POST':
        response = {
            'status': 500,
            'msg': 'Something went wrong in reset password protocol'
        }

        email = request.POST.get('email').lower().strip() if request.POST.get('email') else None
        otp = request.POST.get('otp').lower().strip() if request.POST.get('otp') else None
        password = request.POST.get('password')
        # print('email: ', email, ', otp: ', otp, ', password: ', password)

        if email:
            if authUser.objects.filter(username=email):
                user = authUser.objects.get(username=email)
                generatedOtp = OTP.genOTP()
                template = loader.get_template('mail-view/password-reset-mail-view.html')
                msg = template.render({'name': user.get_full_name(), 'tempPass': generatedOtp.get('otp')})
                mailData = {
                    'sender': 'Team Oolif <no-reply@oolif.xyz>',  # 'CTMela <no-reply@ctmela.com>',
                    'to': [user.username, ],
                    'subject': 'ABC | Password Reset',
                    'msg': msg,
                }
                response = sendmail(mailData=mailData)
                logger.debug('forgetPassword => Mail status: {}'.format(response))
                if response.get('status') == 200:
                    otp, status = OTP.objects.get_or_create(user=user)
                    otp.otp_hash = generatedOtp.get('hash')
                    otp.otp_valid_upto = timezone.now() + timedelta(DEFAULT.PASSWORD_EXPIRY_MIN)
                    otp.save()
                    logger.debug('forgetPassword => otp saved')
                    messages.success(request, "Email sent Successfully")
                    context['user_id'] = user.username
                else:
                    logger.error('forgetPassword =>Error sending Email | Status {}'.format(response))
                    messages.error(request, 'Unable to send Email')
            else:
                logger.error("forgetPassword =>Email doesn't exists| email: {}".format(email))
                messages.error(request, "No account found with this Email")
            # return JsonResponse(response)
            return render(request, 'HOME/forget-password.html', context)
        elif otp:
            user_id = request.POST.get('user_id').strip().lower() if request.POST.get('user_id') else None
            # print(user_id)
            user = User.objects.get(username=user_id)
            response = user.otp.validateOTP(otp)
            # return JsonResponse(response)
            if response.get('status') == 200:
                messages.success(request, response.get('msg'))
                context['token'] = response.get('token')
            else:
                messages.error(request, response.get('msg'))
            context['user_id'] = user.username
            return render(request, 'HOME/forget-password.html', context)
        elif password:
            user_id = request.POST.get('user_id').strip().lower()
            token = request.POST.get('token').strip().lower()
            user = User.objects.get(username=user_id)
            if token == user.otp.otp_hash:
                user.otp.otp_hash = None
                user.otp.save()
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful')
            return redirect('USER:login')
        else:
            response = {
                'status': 500,
                'msg': 'Insufficient data'
            }
            logger.error('forgetPassword => insufficient Data [missing: email / otp / password]')
            # return JsonResponse(response)
            messages.error(request, response.get('msg'))
            return render(request, 'HOME/forget-password.html', context)
    else:
        return render(request, 'HOME/forget-password.html')


@csrf_exempt
def get_cart_json_data(request):
    if request.user.is_authenticated:
        cart = user_utils.get_cart_product_data(request.user.username)
        return JsonResponse({'cart': cart})
    else:
        cart = user_utils.get_cookies_cart_data(request.COOKIES.get('cart'))
        response = JsonResponse({'cart': cart})
        return response

