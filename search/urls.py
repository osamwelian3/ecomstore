from django.urls import include, path, re_path
from search import views
from utils.ssl import ssl_handler

urlpatterns = [
    re_path(r'^results/$', views.results, name='search_results'),
    re_path(r'^autoresults/$', views.autosearch, name='auto_results'),
]
