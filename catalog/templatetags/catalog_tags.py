from django import template
from cart import cart
from catalog.models import Category
from checkout.mpesa_processor import pending_checker, bgprocess
from django.contrib.flatpages.models import FlatPage
import datetime

register = template.Library()


@register.inclusion_tag("tags/cart_box.html")
def cart_box(request):
    paid = ''
    cart_item_count = cart.cart_distinct_item_count(request)
    # Put this in here so that it cuts across all pages and it is related to cart. See function def for comments
    if bgprocess(request) == 0:
        paid = "(Paid)"
    return {'cart_item_count': cart_item_count, 'paid': paid}


@register.inclusion_tag("tags/category_list.html")
def category_list(request_path):
    active_categories = Category.objects.filter(is_active=True)
    return {'active_categories': active_categories, 'request_path': request_path}


@register.inclusion_tag("tags/footer.html")
def footer_links():
    flatpage_list = FlatPage.objects.all()
    return {'flatpage_list': flatpage_list}
