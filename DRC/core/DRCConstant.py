class Constant:
    STATE_CODE_MAP = {
        'AN': 'Andaman and Nicobar Islands',
        'AP': 'Andhra Pradesh',
        'AR': 'Arunachal Pradesh',
        'AS': 'Assam',
        'BR': 'Bihar',
        'CH': 'Chandigarh',
        'CT': 'Chhattisgarh',
        'DN': 'Dadra and Nagar Haveli',
        'DD': 'Daman and Diu',
        'DL': 'Delhi',
        'GA': 'Goa',
        'GJ': 'Gujarat',
        'HR': 'Haryana',
        'HP': 'Himachal Pradesh',
        'JK': 'Jammu and Kashmir',
        'JH': 'Jharkhand',
        'KA': 'Karnataka',
        'KL': 'Kerala',
        'LD': 'Lakshadweep',
        'MP': 'Madhya Pradesh',
        'MH': 'Maharashtra',
        'MN': 'Manipur',
        'ML': 'Meghalaya',
        'MZ': 'Mizoram',
        'NL': 'Nagaland',
        'OR': 'Odisha',
        'PY': 'Puducherry',
        'PB': 'Punjab',
        'RJ': 'Rajasthan',
        'SK': 'Sikkim',
        'TN': 'Tamil Nadu',
        'TG': 'Telangana',
        'TR': 'Tripura',
        'UP': 'Uttar Pradesh',
        'UT': 'Uttarakhand',
        'WB': 'West Bengal',
    }

    STAR_SVG = """
            <svg class="rating-star-svg" xmlns="http://www.w3.org/2000/svg" width="114.021" height="24.145" viewBox="0 0 114.021 24.145">
                <g id="star_{id}" data-name="star_{id}" transform="translate(-1036.64 -906.394)">
                    <path id="Path_1" data-name="Path 1" d="M16.9,3.394,14.014,8.886,16.9,14.377l-6.115-1.049L6.456,17.771l-.892-6.14L0,8.886,5.564,6.14,6.456,0l4.331,4.443Z" transform="matrix(0.966, 0.259, -0.259, 0.966, 1042.609, 907.725)" fill="{color[0]}" stroke="#2ecaa0" stroke-width="1"/>
                    <path id="Path_2" data-name="Path 2" d="M16.9,3.394,14.014,8.886,16.9,14.377l-6.115-1.049L6.456,17.771l-.892-6.14L0,8.886,5.564,6.14,6.456,0l4.331,4.443Z" transform="matrix(0.966, 0.259, -0.259, 0.966, 1065.25, 907.725)" fill="{color[1]}" stroke="#2ecaa0" stroke-width="1"/>
                    <path id="Path_3" data-name="Path 3" d="M16.9,3.394,14.014,8.886,16.9,14.377l-6.115-1.049L6.456,17.771l-.892-6.14L0,8.886,5.564,6.14,6.456,0l4.331,4.443Z" transform="matrix(0.966, 0.259, -0.259, 0.966, 1087.892, 907.725)" fill="{color[2]}" stroke="#2ecaa0" stroke-width="1"/>
                    <path id="Path_4" data-name="Path 4" d="M16.9,3.394,14.014,8.886,16.9,14.377l-6.115-1.049L6.456,17.771l-.892-6.14L0,8.886,5.564,6.14,6.456,0l4.331,4.443Z" transform="matrix(0.966, 0.259, -0.259, 0.966, 1110.533, 907.725)" fill="{color[3]}" stroke="#2ecaa0" stroke-width="1"/>
                    <path id="Path_5" data-name="Path 5" d="M16.9,3.394,14.014,8.886,16.9,14.377l-6.115-1.049L6.456,17.771l-.892-6.14L0,8.886,5.564,6.14,6.456,0l4.331,4.443Z" transform="matrix(0.966, 0.259, -0.259, 0.966, 1133.174, 907.725)" fill="{color[4]}" stroke="#2ecaa0" stroke-width="1"/>
                </g>
            </svg>
        """


class CartConstant:
    ADDED_TO_CART = 'A'
    MAX_NO_OF_PRODUCT_ADDED = 'M'
    REMOVED_FROM_CART = 'R'


class STATUS:
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'


class DEFAULT:
    PASSWORD_EXPIRY_MIN = 1
    NO_OF_OTP_DIGIT = 6


class ErrorCode:
    MIN_NO_OF_PRODUCT_PER_CART_EXCEEDED = 500
    MAX_NO_OF_PRODUCT_PER_CART_EXCEEDED = 501
    NOT_ENOUGH_PRODUCT_IN_STOCK = 502
    INVALID_PRODUCT_ID = 503
    INVALID_ADDRESS_ID = 504
    PRODUCT_NOT_IN_CART = 505
    PRODUCT_NOT_IN_WISHLIST = 506
    QUANTITY_PARAMETER_MISSING = 507
    INVALID_QUANTITY_PARAMETER = 508
    REVIEW_ALREADY_GIVEN = 509
    REVIEW_NOT_GIVEN = 510
    RATING_IS_MANDATORY = 511
    RATING_MUST_BE_A_FLOAT_BW_0_AND_5 = 512
    INVALID_ORDER_ID = 513
    EMPTY_CART = 514
    PAYMENT_METHODE_MISSING = 515
    Expired_ORDER = 516
    INVALID_TRANSACTION_ID = 513
    MISSING_CURRENT_PASSWORD = 514
    MISSING_NEW_PASSWORD = 515
    SAME_PASSWORD_RESTRICTION = 516
    INVALID_CURRENT_PASSWORD = 517
    MISSING_USERNAME = 518
    USER_NOT_FOUND = 519
    MISSING_IDP_KEY = 520
    MISSING_OTP = 521
    INVALID_OTP = 522


class ErrorMessage:
    MIN_NO_OF_PRODUCT_PER_CART_EXCEEDED = 'Minimum of product per cart exceeded'
    MAX_NO_OF_PRODUCT_PER_CART_EXCEEDED = 'Maximum no of product per cart exceeded'
    NOT_ENOUGH_PRODUCT_IN_STOCK = 'Not enough product in stock'
    INVALID_PRODUCT_ID = 'Product id not valid'
    INVALID_ADDRESS_ID = 'Address id not valid'
    PRODUCT_NOT_IN_CART = 'Product is not available in the cart'
    PRODUCT_NOT_IN_WISHLIST = 'Product is not available in the wishlist'
    QUANTITY_PARAMETER_MISSING = "'quantity' is required parameter"
    INVALID_QUANTITY_PARAMETER = "quantity value is not valid"
    REVIEW_ALREADY_GIVEN = "You already reviewed this product"
    REVIEW_NOT_GIVEN = "You haven't reviewed this product yet"
    RATING_IS_MANDATORY = "It's mandatory to leave a rating at least"
    RATING_MUST_BE_A_FLOAT_BW_0_AND_5 = "Rating must be decimal number between 0 and 5"
    INVALID_ORDER_ID = 'Order id not valid'
    EMPTY_CART = 'Cart is empty'
    PAYMENT_METHODE_MISSING = 'Payment methode missing'
    Expired_ORDER = 'Order has been expired'
    INVALID_TRANSACTION_ID = 'Transaction id not valid'
    MISSING_CURRENT_PASSWORD = 'Old password is missing'
    MISSING_NEW_PASSWORD = 'New password is missing'
    SAME_PASSWORD_RESTRICTION = 'New password can\'t be same as previous'
    INVALID_CURRENT_PASSWORD = 'Existing password is incorrect'
    MISSING_USERNAME = 'Username is missing'
    USER_NOT_FOUND = 'No user found'
    MISSING_IDP_KEY = 'IDP key is missing'
    MISSING_OTP = 'OTP is missing'
    INVALID_OTP = 'Invalid OTP'


class CONTROL:
    RESET_PASSWORD_OTP_MAX_MINUTE = 60
