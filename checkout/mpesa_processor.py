import json
from mpesa_api.mpesa_credentials import validated_mpesa_access_token, LipanaMpesaPpassword, MpesaC2bCredential
from cart import cart
import http.client
from django.views.decorators.csrf import csrf_exempt
from mpesa_api.models import MpesaPayment
from .models import Order, OrderItem, PendingMpesa
from .forms import MpesaCheckoutForm
from accounts import profile
from accounts.models import UserProfile


def lipa_na_mpesa_online(request):
    print('ianlipa')
    postdata = request.POST.copy()
    phone = postdata['phone']
    if phone[0] == "0":
        phone = phone.replace('0', '254', 1)
    elif phone[0:4] == "+254":
        phone = phone.replace('+254', '254', 1)
    access_token = validated_mpesa_access_token()
    print(access_token)
    api_url = MpesaC2bCredential.MPESA_URL
    headers = {
        "Authorization": "Bearer %s" % access_token,
        'Content-Type': 'application/json'
    }
    conn = http.client.HTTPSConnection(api_url)
    requestbody = "{\r\n        " \
                  "\"BusinessShortCode\": " + str(LipanaMpesaPpassword.Business_short_code) + ",\r\n        " \
                  "\"Password\": \"" + str(LipanaMpesaPpassword.decode_password) + "\",\r\n        " \
                  "\"Timestamp\": \"" + str(LipanaMpesaPpassword.lipa_time) + "\",\r\n        " \
                  "\"TransactionType\": \"CustomerPayBillOnline\",\r\n        " \
                  "\"Amount\": " + str(cart.cart_subtotal(request)) + ",\r\n        " \
                  "\"PartyA\": " + str(phone) + ",\r\n        " \
                  "\"PartyB\": " + str(LipanaMpesaPpassword.Business_short_code) + ",\r\n        " \
                  "\"PhoneNumber\": " + str(phone) + ",\r\n        " \
                  "\"CallBackURL\": \"https://873e2d51dd67.ngrok.io/api/v1/c2b/callback/\",\r\n        " \
                  "\"AccountReference\": \"SAMIAN LTD\",\r\n        " \
                  "\"TransactionDesc\": \"Test\"\r\n    " \
                  "}"
    conn.request("POST", MpesaC2bCredential.stk_uri, requestbody, headers)
    response = conn.getresponse()
    response_data = response.read()
    print(requestbody)
    print(response_data.decode('utf-8'))
    data = response_data.decode('utf-8')
    values = json.loads(data)
    if 'ResponseCode' in values:
        MerchantRequestID = values['MerchantRequestID']
        CheckoutRequestID = values['CheckoutRequestID']
        ResponseCode = values['ResponseCode']
        ResponseDescription = values['ResponseDescription']
        CustomerMessage = values['CustomerMessage']
        # save the transaction details to PendingMpesa model if the stk push was sent successfully
        if ResponseCode == "0":
            CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
            pending = PendingMpesa()
            pending.phone = phone
            pending.checkoutid = CheckoutRequestID
            pending.cart = request.session[CART_ID_SESSION_KEY]
            pending.save()
            message = query_lipa(request, CheckoutRequestID)
    if 'errorMessage' in values:
        message = 23
    return message


def query_lipa(request, cri):
    access_token = validated_mpesa_access_token()
    print(access_token)
    api_url = MpesaC2bCredential.MPESA_URL
    conn = http.client.HTTPSConnection(api_url)
    request1 = "{\r\n        " \
              "\"BusinessShortCode\": \"" + str(LipanaMpesaPpassword.Business_short_code) + "\",\r\n        " \
              "\"Password\": \"" + str(LipanaMpesaPpassword.decode_password) + "\",\r\n        " \
              "\"Timestamp\": \"" + str(LipanaMpesaPpassword.lipa_time) + "\",\r\n        " \
              "\"CheckoutRequestID\": \"" + str(cri) + "\"\r\n        " \
              "}"
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }
    conn.request("POST", MpesaC2bCredential.querystk, request1, headers)
    response = conn.getresponse()
    response_data = response.read()
    data = response_data.decode('utf-8')
    values = json.loads(data)
    try:
        value = values['errorMessage']
    except Exception:
        value = values['ResponseCode']
    # create a loop that queries the status of the stk push until it finds that the transaction is complete
    while value == "The transaction is being processed":
        conn.request("POST", '/mpesa/stkpushquery/v1/query', request1, headers)
        response = conn.getresponse()
        response_data = response.read()
        data = response_data.decode('utf-8')
        print(data)
        values = json.loads(data)
        if 'ResultDesc' in values:
            break
    # Delete the pending transactions details from pending mpesa if the stk push was not successful other wise keep them for later in response 0
    if values['ResultDesc'] == "DS timeout.":
        CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
        pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
        if pending.count() == 1:
            pending.delete()
        message = 3
    if values['ResultDesc'] == "Request cancelled by user":
        CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
        pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
        if pending.count() == 1:
            pending.delete()
        message = 1
    if values['ResultDesc'] == "The service request is processed successfully.":
        message = 0
    if values['ResultDesc'] == "System busy. The service request is rejected.":
        CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
        pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
        if pending.count() == 1:
            pending.delete()
        message = 26
    if values['ResultDesc'] == "The balance is insufficient for the transaction":
        CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
        pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
        if pending.count() == 1:
            pending.delete()
        message = 90
    print(request1)
    print(data)
    return message


# checks to determin if there is any pending mpesa transaction for the current cart and querys the status if paid
def pending_checker(request):
    CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
    pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
    if pending.count() > 0:
        try:
            message = query_lipa(request, pending[0].checkoutid)
            if message == 0:
                return message
        except Exception:
            # if unable to reach mpesa api servers. connection or url errors
            message = 5
            return message
    return None


# Complete the transaction in the background only if user is authenticated or return the pending checker status for anonymous users
def bgprocess(request):
    if pending_checker(request) == 0 and request.user.is_authenticated:
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        response = process(request)
        order_number = response.get('order_number', 0)
        print(order_number)
        print(response)
        # error_message = response.get('message', '')
        if order_number:
            request.session['order_number'] = order_number
            CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
            pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
            if pending.count() == 1:
                pending.delete()
    return pending_checker(request)


def process(request):
    paid = 0
    cancelled = 1
    timeout = 3
    failed = 5
    busy = 26
    lockfail = 23
    insufficient = 90
    results = {}
    response = ''
    try:
        # if process() was called because of a paid for cart that didn't complete well. This will run
        CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
        pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
        if pending.count() > 0:
            message = pending_checker(request)
        else:
            # This is a fresh transaction
            message = lipa_na_mpesa_online(request)
            print(message)
    except Exception:
        message = 5
    if message == paid:
        transaction_id = "MPESA-" + str(Order.objects.all().count() + 1) + ""
        order = create_order(request, transaction_id)
        results = {"order_number": order.id, 'message': "Payment Successfull. Your Order has been Placed"}
    if message == cancelled:
        results = {"order_number": 0, 'message': "You cancelled the MPESA request. Continue shopping or try"
                                                         " again and enter your MPESA pin to checkout"}
    if message == timeout:
        results = {"order_number": 0, 'message': "You did not enter the MPESA pin on time. Please try again"}
    if message == failed:
        results = {"order_number": 0, 'message': "We are having trouble reaching MPESA, "
                                                  "sorry for any inconvenience caused"}
    if message == busy:
        results = {"order_number": 0, 'message': "MPESA ERROR: System busy. The service request is rejected."}
    if message == lockfail:
        results = {"order_number": 0, 'message': "MPESA ERROR: Unable to lock subscriber,"
                                                 " a transaction is already in process for the current subscriber"}
    if message == insufficient:
        results = {"order_number": 0, 'message': "You do not have sufficient balance in your Mpesa to complete this"
                                                 " transaction"}
    return results


def create_order(request, transaction_id):
    postdata = request.POST.copy()
    CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
    pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
    if request.user.is_authenticated:
        user_profile = profile.retrieve(request)
    else:
        user_profile = ''
    if pending.count() > 0 and request.user.is_authenticated and not request.method == 'POST' and user_profile.shipping_name != '':
        user_profile = profile.retrieve(request)
        print(user_profile.shipping_name)
        order = Order()
        # checkout_form = MpesaCheckoutForm(instance=order)
        # order = checkout_form.save(commit=False)
        order.shipping_name = user_profile.shipping_name
        order.shipping_address_1 = user_profile.shipping_address_1
        order.shipping_address_2 = user_profile.shipping_address_2
        order.shipping_city = user_profile.shipping_city
        order.shipping_zip = user_profile.shipping_zip
        order.shipping_country = user_profile.shipping_country
        order.transaction_id = transaction_id
        order.ip_address = request.META.get('REMOTE_ADDR')
        order.user = None
        if request.user.is_authenticated:
            order.user = request.user
        order.status = Order.SUBMITTED
        order.save()
    else:
        order = Order()
        checkout_form = MpesaCheckoutForm(request.POST, instance=order)
        order = checkout_form.save(commit=False)
        order.billing_name = postdata['shipping_name']
        order.billing_address_1 = postdata['shipping_address_1']
        order.billing_address_2 = postdata['shipping_address_2']
        order.billing_city = postdata['shipping_city']
        order.billing_zip = postdata['shipping_zip']
        order.billing_country = postdata['shipping_country']
        order.transaction_id = transaction_id
        order.ip_address = request.META.get('REMOTE_ADDR')
        order.user = None
        if request.user.is_authenticated:
            order.user = request.user
        order.status = Order.SUBMITTED
        order.save()
    # if the order save succeeded
    if order.pk:
        cart_items = cart.get_cart_items(request)
        for ci in cart_items:
            # create order item for each cart item
            oi = OrderItem()
            oi.order = order
            oi.quantity = ci.quantity
            oi.price = ci.price  # now using @property
            oi.product = ci.product
            oi.save()
        # all set, empty cart
        cart.empty_cart(request)
        # save profile info for future orders
        if request.user.is_authenticated and not pending_checker(request) == 0:
            profile.set(request)
    # return the new order object
    return order
