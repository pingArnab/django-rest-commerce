from DRC.settings import PROJECT_NAME


class DEFAULT:
    COD = {
        'id': 'pod',
        'name': 'Pay On Delivery',
        'image': '/media/features/pod',
        'description': 'Pay on Delivery (Cash/Card) payment method includes Cash on Delivery (COD) as well as Debit '
                       'card / Credit card / Net banking payments at your doorstep. '
    }

    SITE_DELIVERED = {
        'id': f'{PROJECT_NAME}-delivered',
        'name': f'{PROJECT_NAME} Delivered',
        'image': f'/media/features/{PROJECT_NAME}-delivered',
        'description': f'{PROJECT_NAME} directly manages delivery for this product. Order delivery tracking to your doorstep '
                       'is available. '
    }

    NO_CONTACT_DELIVERY = {
        'id': 'no-contact-delivery',
        'name': 'No-Contact Delivery',
        'image': '/media/features/no-contact-delivery',
        'description': 'Delivery Associate will place the order on your doorstep and step back to maintain a 2-meter '
                       'distance. No customer signatures are required at the time of delivery. For Pay-on-Delivery '
                       'orders, we recommend paying using Credit card/Debit card/Netbanking via the pay-link sent via '
                       'SMS at the time of delivery. To pay by cash, place cash on top of the delivery box and step '
                       'back. '
    }
