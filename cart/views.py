from django.shortcuts import render, render_to_response, reverse
from django.template import RequestContext
from cart import cart
from django.views.decorators.csrf import csrf_exempt
from checkout import checkout
from ecomstore import settings
from django.http import HttpResponseRedirect
from checkout.mpesa_processor import pending_checker, bgprocess
from stats import stats

from django.template.loader import render_to_string
import json as simplejson
from django.http import HttpResponse


# Create your views here.
@csrf_exempt
def show_cart(request, template_name="cart/cart.html"):
    request.session.set_test_cookie()
    next1 = ''
    recent_views = stats.recommended_from_views(request)
    if request.method == 'POST':
        print(request.session['cart_id'])
        postdata = request.POST.copy()
        if postdata['submit'] == 'Remove':
            if pending_checker(request) == 0:
                url = reverse('show_checkout', args=['Lipa'])
                return HttpResponseRedirect(url)
            cart.remove_from_cart(request)
            next1 = request.GET.get('next', '')
            if len(next1) > 0:
                url = reverse('show_checkout', args=[next1])
                return HttpResponseRedirect(url)
        if postdata['submit'] == 'Update':
            if pending_checker(request) == 0:
                url = reverse('show_checkout', args=['Lipa'])
                return HttpResponseRedirect(url)
            try:
                int(postdata['quantity'])
                cart.update_cart(request)
                next1 = request.GET.get('next', '')
                if len(next1) > 0:
                    url = reverse('show_checkout', args=[next1])
                    return HttpResponseRedirect(url)
            except:
                if cart.cart_distinct_item_count(request) > 0:
                    qerror = 'Invalid Quantity Value'
        if postdata['submit'] == 'Card Checkout':
            checkout_url = checkout.get_checkout_url(request)
            return HttpResponseRedirect(checkout_url)
        if postdata['submit'] == 'Mpesa Checkout':
            checkout_url = checkout.get_checkout_url(request)
            return HttpResponseRedirect(checkout_url)
    if len(next1) > 0:
        url = reverse('show_checkout', args=[next1])
        return HttpResponseRedirect(url)
    cart_items = cart.get_cart_items(request)
    page_title = 'Shopping Cart'
    cart_subtotal = cart.cart_subtotal(request)
    return render(request, template_name, locals(), RequestContext(request))


def update_cart(request):
    pending = ''
    qerror = ''
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    reload = 'location.reload(true);'
    if request.method == 'POST':
        postdata = request.POST.copy()
        page_title = postdata['page_title']
        if postdata['submit'] == 'Remove':
            if pending_checker(request) == 0:
                pending = 'You have a pending transaction on this cart'
            else:
                cart.remove_from_cart(request)
        if postdata['submit'] == 'Update':
            if pending_checker(request) == 0:
                pending = 'You have a pending transaction on this cart'
            else:
                try:
                    int(postdata['quantity'])
                    cart.update_cart(request)
                except:
                    if cart.cart_distinct_item_count(request) > 0:
                        qerror = 'Invalid Quantity Value'
    paid = ''
    subtotal = cart.cart_subtotal(request)
    cart_items = cart.get_cart_items(request)
    cart_item_count = cart.cart_distinct_item_count(request)
    # Put this in here so that it cuts across all pages and it is related to cart. See function def for comments
    if bgprocess(request) == 0:
        paid = "(Paid)"
    cart_template = "tags/cart_box.html"
    cart_html = render_to_string(cart_template, locals())
    if len(pending) == 0 and len(qerror) == 0:
        cart_items = cart.get_cart_items(request)
        cart_subtotal = cart.cart_subtotal(request)
        template = "cart/cart_preview.html"
        html = render_to_string(template, locals())
        print(html)
        response = simplejson.dumps({'success': 'True', 'html': html, 'cart_html': cart_html})
    else:
        html = '<p class="errorlist">{{ qerror }}</p>'
        response = simplejson.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
