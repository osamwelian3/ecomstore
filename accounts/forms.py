from django import forms
from accounts.models import UserProfile


class UserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
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
        self.fields['billing_state'].widget.attrs['size'] = ''
        self.fields['billing_state'].widget.attrs['size'] = ''
        self.fields['billing_zip'].widget.attrs['size'] = '6'

    class Meta:
        model = UserProfile
        exclude = ('user',)
