import logging
import traceback

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User as AuthUser
from DRC.core.DRCConstant import CONTROL
from HOME.models import OTP
from .serializers import UserProfileSerializer, UserAddressSerializer, CartSerializer
from PRODUCT.serializers import ProductListSerializer
from DRC.core.exceptions import ErrorResponse
from DRC.core.permissions import UserOnly, IsNotAuthenticated
from USER.models import Cart, UserAddress, UserProfile
from PRODUCT.models import Product
from DRC.core.DRCConstant import ErrorMessage, ErrorCode
from DRC.core.mail import UserVerificationMail, PasswordResetMail
from DRC.settings import DOMAIN_NAME
from DRC.settings import PROJECT_NAME


__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


@api_view(['POST'])
def signup(request):
    first_name = request.data.get('first_name').strip() if request.data.get('first_name') else None
    last_name = request.data.get('last_name').strip() if request.data.get('last_name') else None
    email = request.data.get('email').strip() if request.data.get('email') else None
    phone_no = request.data.get('phone_no').strip() if request.data.get('phone_no') else None
    password = request.data.get('password')
    try:
        user = AuthUser.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        userprofile = UserProfile.objects.create(
            user_id=user.id,
            ph_no=phone_no,
            verified=False
        )
        userprofile.save()
        # Send mail
        key = userprofile.get_verification_key()
        mail = UserVerificationMail(
            receiver=email,
            name=first_name,
            url=f'https://{DOMAIN_NAME}/user/verify/?username={user.username}&key={key}'
        )
        return mail.send()
    except Exception as ex:
        return ErrorResponse(code=500, msg=ex.__str__(), details=ex.__str__()).response


@api_view(['GET'])
@permission_classes([IsAuthenticated, UserOnly])
def resend_validation_key_email(request):
    user: AuthUser = request.user
    if user.userprofile.verified:
        return ErrorResponse(code=404, msg='Invalid URL').response
    try:
        mail = UserVerificationMail(
            receiver=user.email,
            name=user.first_name,
            url=f'https://ctmela.com/user/verify/?username={user.username}&key={user.userprofile.verification_key}'
        )
        return mail.send()
    except Exception as ex:
        return ErrorResponse(code=500, msg=ex.__str__(), details=ex.__str__()).response


@api_view(['GET'])
def verify_validation_key(request):
    username = request.query_params.get('username').strip() if request.query_params.get('username') else ''
    key = request.query_params.get('key').strip() if request.query_params.get('key') else ''
    if UserProfile.objects.filter(user__username=username):
        userprofile = UserProfile.objects.get(user__username=username)
        if userprofile.validate_verification_key(key):
            return Response({
                'status': 'success',
                'username': userprofile.user.username
            })
    return ErrorResponse(code=404, msg='Invalid URL').response


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, UserOnly])
def user_profile(request):
    user: AuthUser = request.user
    if request.method == 'PUT':
        if request.data.get('first_name'):
            user.first_name = request.data.get('first_name').strip()
        if request.data.get('last_name'):
            user.last_name = request.data.get('last_name').strip()
        if request.data.get('phone_no'):
            user.userprofile.ph_no = request.data.get('phone_no').strip()
            user.userprofile.save()
        user.save()

    if request.method == 'DELETE':
        user.delete()
        return Response({
            'status': 'success',
            'details': 'User successfully deleted'
        })

    return Response(
        UserProfileSerializer(user, many=False).data
    )


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, UserOnly])
def user_address(request, address_id: str = None):
    user: AuthUser = request.user
    # Add Address
    if request.method == 'POST':
        try:
            address = UserAddress.objects.create(
                user_id=user.id,

                name=request.data.get('name'),
                address_line_1=request.data.get('address_line_1'),
                address_line_2=request.data.get('address_line_2'),
                landmark=request.data.get('landmark'),
                city=request.data.get('city'),
                pin=request.data.get('pin'),

                state=request.data.get('state'),
                country=request.data.get('country'),

                ph_no=request.data.get('ph_no'),

                address_type=request.data.get('address_type'),
            )
            address.save()
        except Exception as ex:
            return ErrorResponse(
                code=403,
                msg=str(ex)
            ).response

    # Delete Address
    if request.method == 'DELETE':
        if not UserAddress.objects.filter(user_id=user.id, id=address_id):
            return ErrorResponse(
                code=ErrorCode.INVALID_ADDRESS_ID,
                msg=ErrorMessage.INVALID_ADDRESS_ID
            ).response
        UserAddress.objects.filter(user_id=user.id, id=address_id).delete()

    # Get Address
    address = user.useraddress_set.all()
    return Response(
        UserAddressSerializer(address, many=True).data
    )


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, UserOnly])
def user_wishlist(request, product_id: str = None):
    user: AuthUser = request.user

    # Add to wishlist
    if request.method == 'POST':
        if not Product.objects.filter(product_id=product_id):
            return ErrorResponse(
                code=ErrorCode.INVALID_PRODUCT_ID,
                msg=ErrorMessage.INVALID_PRODUCT_ID
            ).response
        user.userprofile.wishlist.add(product_id)
        user.userprofile.save()

    # Delete from wishlist
    if request.method == 'DELETE':
        if not user.userprofile.wishlist.filter(product_id=product_id):
            return ErrorResponse(
                code=ErrorCode.PRODUCT_NOT_IN_WISHLIST,
                msg=ErrorMessage.PRODUCT_NOT_IN_WISHLIST
            ).response
        user.userprofile.wishlist.remove(product_id)
        user.userprofile.save()

    # Get wishlist
    wishlist = user.userprofile.wishlist.all()
    # if not wishlist:
    #     return ErrorResponse(code=404, msg='No address found').response
    return Response(
        ProductListSerializer(wishlist, many=True, context={'user': request.user}).data
    )


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, UserOnly])
def user_cart(request, product_id: str = None):
    FUNCTION_NAME = 'user_cart'
    user: AuthUser = request.user
    logger.debug(f'{FUNCTION_NAME} -> Request from user: {AuthUser}')
    # Add to cart
    if request.method == 'POST':
        if not Product.objects.filter(product_id=product_id):
            return ErrorResponse(
                code=ErrorCode.INVALID_PRODUCT_ID,
                msg=ErrorMessage.INVALID_PRODUCT_ID
            ).response
        quantity_param: str = request.query_params.get('quantity')
        quantity = int(quantity_param) if (quantity_param and quantity_param.isdecimal()) else 1
        cart, status = Cart.objects.get_or_create(
            user_id=user.id,
            product_id=product_id
        )
        try_quantity = quantity + (cart.quantity, 0)[bool(status)]
        addable_quantity, error_res = cart.product.addable_quantity_checker(try_quantity)
        if error_res:
            return error_res.response
        cart.quantity = addable_quantity
        cart.save()

    # Update Quantity
    if request.method == 'PUT':
        if not Cart.objects.filter(product_id=product_id, user_id=user.id):
            return ErrorResponse(
                code=ErrorCode.PRODUCT_NOT_IN_CART,
                msg=ErrorMessage.PRODUCT_NOT_IN_CART
            ).response
        quantity_param: str = request.query_params.get('quantity')
        if not quantity_param:
            return ErrorResponse(ErrorCode.QUANTITY_PARAMETER_MISSING, ErrorMessage.QUANTITY_PARAMETER_MISSING).response
        elif not quantity_param.isdecimal():
            return ErrorResponse(ErrorCode.INVALID_QUANTITY_PARAMETER, ErrorMessage.INVALID_QUANTITY_PARAMETER).response
        else:
            try_quantity = int(quantity_param)
        cart = Cart.objects.get(user_id=user.id, product_id=product_id)
        addable_quantity, error_res = cart.product.addable_quantity_checker(try_quantity)
        if error_res:
            return error_res.response
        cart.quantity = addable_quantity
        cart.save()

    # Delete from cart
    if request.method == 'DELETE':
        Cart.objects.filter(
            user__username=user.username,
            product_id=product_id
        ).delete()

    # Get cart
    cart_qs = user.cart_set.all()
    return Response({
        'products': CartSerializer(cart_qs, many=True).data,
        'product_count': Cart.total_product_by_username(user.username),
        'total_price': Cart.total_amount_by_username(user.username),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, UserOnly])
def add_all_user_cart(request):
    if not request.data:
        return ErrorResponse(code=400, msg='No product to add in cart')
    res = []
    for cart_data in request.data:
        product_id = cart_data.get('product_id').strip() if cart_data.get('product_id') else None
        quantity = cart_data.get('quantity')
        if not (product_id and quantity and type(quantity) == int and Product.objects.filter(product_id=product_id)):
            res.append({
                'product_id': product_id, 'quantity': quantity, 'status': False,
                'details': 'Invalid product_id and quantity pair'
            })
            continue
        try:
            new_cart, created = Cart.objects.get_or_create(
                user_id=request.user.id,
                product_id=Product.objects.get(product_id=product_id).product_id
            )
            try_quantity = quantity
            addable_quantity, error_res = new_cart.product.addable_quantity_checker(try_quantity)
            if error_res:
                if created:
                    new_cart.delete()
                res.append({'product_id': product_id, 'quantity': quantity, 'status': False, 'details': error_res.msg})
                continue
            new_cart.quantity = addable_quantity
            new_cart.save()
            res.append({'product_id': product_id, 'quantity': quantity, 'status': True})
        except Exception as ex:
            res.append({'product_id': product_id, 'quantity': quantity, 'status': False, 'details': ex.__str__()})

    return Response(res)


# Password Change
@api_view(['PUT'])
@permission_classes([IsAuthenticated, UserOnly])
def change_password(request):
    user: AuthUser = request.user

    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password:
        return ErrorResponse(code=ErrorCode.MISSING_CURRENT_PASSWORD,
                             msg=ErrorMessage.MISSING_CURRENT_PASSWORD).response
    if not new_password:
        return ErrorResponse(code=ErrorCode.MISSING_NEW_PASSWORD, msg=ErrorMessage.MISSING_NEW_PASSWORD).response

    if user.check_password(current_password):
        if current_password != new_password:
            user.set_password(new_password)
            user.save()
            return Response({'status': 'success'})
        else:
            return ErrorResponse(
                code=ErrorCode.SAME_PASSWORD_RESTRICTION,
                msg=ErrorMessage.SAME_PASSWORD_RESTRICTION
            ).response
    else:
        return ErrorResponse(
            code=ErrorCode.INVALID_CURRENT_PASSWORD,
            msg=ErrorMessage.INVALID_CURRENT_PASSWORD
        ).response


# Reset Change
@api_view(['POST', 'PUT'])
@permission_classes([IsNotAuthenticated])
def reset_password(request):
    if request.method == 'POST':
        username = request.data.get('username')
        if not username:
            return ErrorResponse(code=ErrorCode.MISSING_USERNAME, msg=ErrorMessage.MISSING_USERNAME).response
        if not AuthUser.objects.filter(username=username.strip()):
            return ErrorResponse(code=ErrorCode.USER_NOT_FOUND, msg=ErrorMessage.USER_NOT_FOUND).response
        try:
            user = AuthUser.objects.get(username=username.strip())
            if user.is_superuser:
                return ErrorResponse(code=400, msg='Resetting password is not authorised').response
            otp = OTP.genOTP()
            otp_obj, status = OTP.objects.get_or_create(user_id=user.id, type=OTP.TYPE.RESET_PASSWORD)
            otp_obj.otp_hash = otp.get('hash')
            otp_obj.set_validity(minutes=CONTROL.RESET_PASSWORD_OTP_MAX_MINUTE)
            mail = PasswordResetMail(
                receiver=user.email,
                name=user.first_name,
                otp=otp.get('otp')
            )
            mail.send()
            otp_obj.save()
            return Response({
                'username': user.username,
                'idp_key': otp_obj.idp_key
            })
        except Exception as ex:
            traceback.print_exc()
            return ErrorResponse(code=500, msg=ex.__str__(), details=ex.__str__()).response

    if request.method == 'PUT':
        username = request.data.get('username')
        idp_key = request.data.get('idp_key')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not username:
            return ErrorResponse(code=ErrorCode.MISSING_USERNAME, msg=ErrorMessage.MISSING_USERNAME).response
        if not idp_key:
            return ErrorResponse(code=ErrorCode.MISSING_IDP_KEY, msg=ErrorMessage.MISSING_IDP_KEY).response
        if not otp:
            return ErrorResponse(code=ErrorCode.MISSING_OTP, msg=ErrorMessage.MISSING_OTP).response
        if not new_password:
            return ErrorResponse(code=ErrorCode.MISSING_NEW_PASSWORD, msg=ErrorMessage.MISSING_NEW_PASSWORD).response

        if not OTP.objects.filter(user__username=username.strip(), idp_key=idp_key):
            return ErrorResponse(code=400, msg='Invalid username or IDP Key').response

        otp_obj: OTP = OTP.objects.get(user__username=username.strip(), idp_key=idp_key)
        validate: dict = otp_obj.validateOTP(otp)
        if validate.get('status') == 200:
            if otp_obj.user.check_password(new_password):
                return ErrorResponse(
                    code=ErrorCode.SAME_PASSWORD_RESTRICTION,
                    msg=ErrorMessage.SAME_PASSWORD_RESTRICTION
                ).response
            otp_obj.user.set_password(new_password)
            otp_obj.user.save()
            otp_obj.delete()
            return Response({'status': 'success'})
        else:
            return ErrorResponse(code=ErrorCode.INVALID_OTP, msg=validate.get('msg')).response
