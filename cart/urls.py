from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r'^$', views.show_cart, name='show_cart'),
    re_path(r'^update_cart/$', views.update_cart, name='update_cart'),
]
