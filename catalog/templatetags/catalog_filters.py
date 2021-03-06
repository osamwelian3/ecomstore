from django import template
import locale
from decimal import Decimal

register = template.Library()


@register.filter(name='currency')
def currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'en_KE.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    value = Decimal(value)
    loc = locale.localeconv()
    return 'Ksh ' + str(value)  # return locale.currency(value, loc['currency_symbol'], grouping=True)


@register.filter(name='div')
def div(value, arg):
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            output = value/arg
            if output.is_integer():
                return output
            else:
                return False
        else:
            return False
    except Exception as e:
        error = e
        return False
