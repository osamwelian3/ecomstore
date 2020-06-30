from catalog.models import Category
from checkout.mpesa_processor import pending_checker
from cart.cart import cart_distinct_item_count
from ecomstore import settings


def ecomstore(request):
    return {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
        'MEDIA_URL': settings.MEDIA_URL,
        'request': request,
        'cart_item_count': cart_distinct_item_count(request),
        'pending': pending_checker(request)
    }
