from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    re_path(r'^$', views.index, {}, name='catalog_home'),
    re_path(r'^category/(?P<category_slug>[-\w]+)/$', views.show_category, name='catalog_category'),
    re_path(r'^product/(?P<product_slug>[-\w]+)/$', views.show_product, name='catalog_product'),
    re_path(r'^review/product/add/$', views.add_review, name='add_review'),
    re_path(r'^tag/product/add/$', views.add_tag, name='add_tag'),
    re_path(r'^tag_cloud/$', views.tag_cloud, name='tag_cloud'),
    re_path(r'^tag/(?P<tag>[-\w]+)/$', views.tag, name='tag'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print(urlpatterns)
