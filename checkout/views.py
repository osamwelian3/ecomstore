from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse
from django.http import HttpResponseRedirect

from checkout.forms import CheckoutForm, MpesaCheckoutForm
from checkout.models import Order, OrderItem, PendingMpesa
from checkout import checkout
from cart import cart
from . import mpesa_processor
from django.views.decorators.csrf import csrf_exempt
from accounts import profile


# Create your views here.
@csrf_exempt
def show_checkout(request, checkout_type, template_name="checkout/checkout.html"):
    # print(request.POST.copy())
    # request1 = locals()
    # print(request1)
    print('ian')
    print(request.method)
    error_message = ''
    if cart.is_empty(request):
        cart_url = reverse('show_cart')
        return HttpResponseRedirect(cart_url)
    if request.method == 'POST' and request.POST.copy()['payment'] == "Mpesa Payment" or request.method == 'POST' and\
            request.POST.copy()['phone2'] != '' and request.POST.copy()['credit_card_number'] == '' and\
            request.POST.copy()['credit_card_cvv'] == '':
        postdata = request.POST.copy()
        postdata['billing_name'] = postdata['shipping_name']
        postdata['billing_address_1'] = postdata['shipping_address_1']
        postdata['billing_address_2'] = postdata['shipping_address_2']
        postdata['billing_city'] = postdata['shipping_city']
        postdata['billing_zip'] = postdata['shipping_zip']
        postdata['billing_country'] = postdata['shipping_country']
        postdata['payment'] = postdata['payment']
        form = CheckoutForm(postdata)
        if form.is_valid():
            response = mpesa_processor.process(request)
            order_number = response.get('order_number', 0)
            error_message = response.get('message', '')
            if order_number:
                request.session['order_number'] = order_number
                receipt_url = reverse('checkout_receipt')
                CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
                pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
                if pending.count() == 1:
                    pending.delete()
                return HttpResponseRedirect(receipt_url)
        else:
            error_message = "Correct the errors below"
    if request.method == 'POST' and request.POST.copy()['payment'] == "Place Order" or request.method == 'POST' and\
            request.POST.copy()['credit_card_number'] != '' and request.POST.copy()['credit_card_cvv'] != '' and\
            request.POST.copy()['phone2'] == '':
        postdata = request.POST.copy()
        if 'billing' in request.POST.copy():
            if postdata['billing_name'] == '':
                error_message = 'Input billing name'
            if postdata['billing_address_1'] == '':
                error_message = 'Input billing address'
            if postdata['billing_city'] == '':
                error_message = 'Input billing city'
            if postdata['billing_zip'] == '':
                error_message = 'Input billing zip/postal code'
            if postdata['billing_country'] == '':
                error_message = 'Input billing country'
        if not 'billing' in request.POST.copy():
            postdata['billing_name'] = postdata['shipping_name']
            postdata['billing_address_1'] = postdata['shipping_address_1']
            postdata['billing_address_2'] = postdata['shipping_address_2']
            postdata['billing_city'] = postdata['shipping_city']
            postdata['billing_zip'] = postdata['shipping_zip']
            postdata['billing_country'] = postdata['shipping_country']
        form = CheckoutForm(postdata)
        # print(postdata)
        # print(form)
        # print("frm")
        if form.is_valid():
            response = checkout.process(request)
            order_number = response.get('order_number', 0)
            error_message = response.get('message', '')
            if order_number:
                request.session['order_number'] = order_number
                receipt_url = reverse('checkout_receipt')
                return HttpResponseRedirect(receipt_url)
        else:
            error_message = 'Correct the errors below'
    else:
        if request.user.is_authenticated:
            user_profile = profile.retrieve(request)
            form = CheckoutForm(instance=user_profile)
        else:
            form = CheckoutForm()
            """if request.method == 'GET' and checkout_type != 'Lipa' and checkout_type != 'PendingLipa':
                form = CheckoutForm(instance=user_profile)
            if request.method == 'POST' and checkout_type == "Lipa":
                postdata = request.POST.copy()
                form = MpesaCheckoutForm(postdata)
            if request.GET and checkout_type == "Lipa":
                form = MpesaCheckoutForm(instance=user_profile)
            if request.GET and checkout_type == "PendingLipa":
                form = MpesaCheckoutForm(instance=user_profile)"""

        if request.method == 'POST' and checkout_type == "Lipa":
            postdata = request.POST.copy()
            # print(postdata)
            form = CheckoutForm(postdata)
            # print(request.POST.copy()['payment'])
            if request.POST.copy()['payment'] == 'on' and postdata['phone2'] == '' and postdata['credit_card_number']\
                    == '' and postdata['credit_card_cvv'] == '':
                empty1 = 'Please select payment method'
                error_message = 'Correct the errors below'
            if request.POST.copy()['payment'] == 'on' and postdata['phone2'] != '' and postdata['credit_card_number']\
                    != '' or postdata['credit_card_cvv'] != '':
                empty1 = 'Please select payment method'
                error_message = 'Correct the errors below'
        if request.GET and checkout_type == "Lipa":
            form = CheckoutForm()
            """if request.method == 'POST' and checkout_type == "Lipa":
                postdata = request.POST.copy()
                form = MpesaCheckoutForm(postdata)
            if request.GET and checkout_type == "Lipa":
                form = MpesaCheckoutForm()
            if request.GET and checkout_type == "PendingLipa":
                form = MpesaCheckoutForm()"""
    page_title = 'Checkout'
    cart_items = cart.get_cart_items(request)
    cart_subtotal = cart.cart_subtotal(request)
    checkout_type = checkout_type
    return render(request, template_name, locals(), RequestContext(request))


def receipt(request, template_name='checkout/receipt.html'):
    order_number = request.session.get('order_number', '')
    if order_number:
        order = Order.objects.filter(id=order_number)[0]
        order_status = dict(order.ORDER_STATUSES)[order.status]
        order_items = OrderItem.objects.filter(order=order)
        del request.session['order_number']
    else:
        cart_url = reverse('show_cart')
        return HttpResponseRedirect(cart_url)
    page_title = 'Receipt'
    return render(request, template_name, locals(), RequestContext(request))
