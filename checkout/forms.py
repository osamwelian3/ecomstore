from django import forms
from checkout.models import Order
import datetime
import re


def cc_expire_years():
    current_year = datetime.datetime.now().year
    years = range(current_year, current_year+12)
    return [(str(x), str(x)) for x in years]


def cc_expire_months():
    months = []
    for month in range(1, 13):
        if len(str(month)) == 1:
            numeric = '0' + str(month)
        else:
            numeric = str(month)
        months.append((numeric, datetime.date(2009, month, 1).strftime('%B')))
    return months


CARD_TYPES = (('Mastercard','Mastercard'),
              ('VISA','VISA'),
              ('AMEX','AMEX'),
              ('Discover','Discover'),)


def strip_non_numbers(data):
    """  gets rid of all non-number characters """
    non_numbers = re.compile('\D')
    return non_numbers.sub('', data)


# Gateway test credit cards won't pass this validation
def cardLuhnChecksumIsValid(card_number):
    """ # checks to make sure that the card passes a luhn mod-10 checksum """
    """sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range(0, num_digits):
        digit = int(card_number[count])
        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit
    return (sum % 10) == 0"""


class CheckoutForm(forms.ModelForm):
    payment = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        # override default attributes
        for field in self.fields:
            self.fields[field].widget.attrs['size'] = ''
            self.fields[field].widget.attrs['class'] = 'input'
        self.fields['phone'].widget.attrs['placeholder'] = '*Phone'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['shipping_name'].widget.attrs['placeholder'] = '*Full Name'
        self.fields['shipping_address_1'].widget.attrs['placeholder'] = '*Address Line 1'
        self.fields['shipping_address_2'].widget.attrs['placeholder'] = 'Address Line 2'
        self.fields['shipping_city'].widget.attrs['placeholder'] = '*City/Town'
        self.fields['shipping_state'].widget.attrs['placeholder'] = 'Estate/Village'
        self.fields['shipping_zip'].widget.attrs['placeholder'] = '*Zip/Postal Code'
        self.fields['shipping_country'].widget.attrs['placeholder'] = '*Country'
        self.fields['billing_name'].widget.attrs['placeholder'] = '*Billing Name'
        self.fields['billing_address_1'].widget.attrs['placeholder'] = '*Address Line 1'
        self.fields['billing_address_2'].widget.attrs['placeholder'] = 'Address Line 2'
        self.fields['billing_city'].widget.attrs['placeholder'] = '*Billing City/Town'
        self.fields['billing_state'].widget.attrs['placeholder'] = 'Billing State/Province'
        self.fields['billing_zip'].widget.attrs['placeholder'] = '*Billing Zip/Postal Code'
        self.fields['billing_country'].widget.attrs['placeholder'] = '*Billing Country'
        self.fields['shipping_state'].widget.attrs['size'] = ''
        self.fields['shipping_state'].widget.attrs['size'] = ''
        self.fields['shipping_zip'].widget.attrs['size'] = '6'
        self.fields['billing_state'].widget.attrs['size'] = '3'
        self.fields['billing_state'].widget.attrs['size'] = '3'
        self.fields['billing_zip'].widget.attrs['size'] = '6'
        self.fields['credit_card_type'].widget.attrs['size'] = '1'
        self.fields['credit_card_expire_year'].widget.attrs['size'] = '1'
        self.fields['credit_card_expire_month'].widget.attrs['size'] = '1'
        self.fields['credit_card_cvv'].widget.attrs['size'] = '5'
        self.fields['credit_card_type'].widget.attrs['class'] = 'form-control'
        self.fields['credit_card_expire_year'].widget.attrs['class'] = 'form-control'
        self.fields['credit_card_expire_month'].widget.attrs['class'] = 'form-control'
        self.fields['phone2'].widget.attrs['placeholder'] = 'Mpesa Phone Number'
        self.fields['credit_card_number'].widget.attrs['placeholder'] = 'Credit Card Number'
        self.fields['credit_card_cvv'].widget.attrs['placeholder'] = 'CVV'

    class Meta:
        model = Order
        exclude = ('status', 'ip_address', 'user', 'transaction_id',)

    field_order = ['payment', 'billing_name']

    phone2 = forms.CharField(required=False)
    credit_card_number = forms.CharField(required=False)
    credit_card_type = forms.CharField(widget=forms.Select(choices=CARD_TYPES), required=False)
    credit_card_expire_month = forms.CharField(widget=forms.Select(choices=cc_expire_months()), required=False)
    credit_card_expire_year = forms.CharField(widget=forms.Select(choices=cc_expire_years()), required=False)
    credit_card_cvv = forms.CharField(required=False)

    """def clean_credit_card_number(self):
        cc_number = self.cleaned_data['credit_card_number']
        stripped_cc_number = strip_non_numbers(cc_number)
        if not cardLuhnChecksumIsValid(stripped_cc_number):
            raise forms.ValidationError('The credit card you entered is invalid.')"""

    def clean_payment(self):
        payment = self.cleaned_data['payment']
        return payment

    def clean_credit_card_cvv(self):
        payment = self.cleaned_data['payment']
        cvv = self.cleaned_data['credit_card_cvv']
        if len(cvv) < 3 and payment == 'Place Order':
            raise forms.ValidationError('Enter a valid CVV')
        return self.cleaned_data['credit_card_cvv']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        stripped_phone = strip_non_numbers(phone)
        if len(stripped_phone) < 10:
            raise forms.ValidationError('Enter a valid phone number.(e.g. 07XX XXX XXX)')
        return self.cleaned_data['phone']

    def clean_phone2(self):
        payment = self.cleaned_data['payment']
        phone2 = self.cleaned_data['phone2']
        stripped_phone = strip_non_numbers(phone2)
        if len(stripped_phone) < 10 and payment == 'Mpesa Payment':
            raise forms.ValidationError('Enter a valid MPESA phone number.(e.g. 07XX XXX XXX)')
        return self.cleaned_data['phone2']

    def clean_billing_name(self):
        payment = self.cleaned_data['payment']
        billing_name = self.cleaned_data['billing_name']
        if len(billing_name) < 2 and payment == 'Place Order':
            raise forms.ValidationError('Enter a valid Billing Name')
        return self.cleaned_data['billing_name']

    def clean_billing_address_1(self):
        payment = self.cleaned_data['payment']
        billing_address_1 = self.cleaned_data['billing_address_1']
        if len(billing_address_1) < 2 and payment == 'Place Order':
            raise forms.ValidationError('Enter a valid Billing Address')
        return self.cleaned_data['billing_address_1']

    def clean_billing_city(self):
        payment = self.cleaned_data['payment']
        billing_city = self.cleaned_data['billing_city']
        if len(billing_city) < 2 and payment == 'Place Order':
            raise forms.ValidationError('Enter a valid Billing City')
        return self.cleaned_data['billing_city']

    def clean_billing_zip(self):
        payment = self.cleaned_data['payment']
        billing_zip = self.cleaned_data['billing_zip']
        if len(billing_zip) < 2 and payment == 'Place Order':
            raise forms.ValidationError('Enter a valid Billing Zip/Postal Code')
        return self.cleaned_data['billing_zip']

    def clean_billing_country(self):
        payment = self.cleaned_data['payment']
        billing_country = self.cleaned_data['billing_country']
        if len(billing_country) < 2 and payment == 'Place Order':
            raise forms.ValidationError('Enter a valid Billing Country')
        return self.cleaned_data['billing_country']


class MpesaCheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('status', 'ip_address', 'user', 'transaction_id', 'billing_name', 'billing_address_1',
                   'billing_address_2', 'billing_city', 'billing_state', 'billing_zip', 'billing_country',)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        stripped_phone = strip_non_numbers(phone)
        if len(stripped_phone) < 10:
            raise forms.ValidationError('Enter a valid phone number.(e.g. 07XX XXX XXX)')
        return self.cleaned_data['phone']
