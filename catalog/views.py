from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.urls import reverse
from cart import cart
from django.http import HttpResponseRedirect
from .forms import ProductAddToCartForm, ProductReviewForm
from django.views.decorators.csrf import csrf_exempt
from checkout.mpesa_processor import pending_checker
from stats import stats
from ecomstore.settings import PRODUCTS_PER_ROW

from catalog.models import Category, Product, ProductReview
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import json as simplejson
from django.http import HttpResponse

import tagging
from tagging.models import Tag, TaggedItem
import tagging.utils

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def index(request, template_name="catalog/index.html"):
    search_recs = stats.recommended_from_search(request)
    featured = Product.featured.all()[0:PRODUCTS_PER_ROW]
    recently_viewed = stats.get_recently_viewed(request)
    view_recs = stats.recommended_from_views(request)
    all_view_recs = stats.recommended_from_all_views(request)
    print(search_recs)
    page_title = 'Musical Instruments and Sheet Music for Musicians'
    context = {
        'page_title': page_title,
    }
    # context2 = RequestContext(request, context)
    request.session.set_test_cookie()
    return render(request, template_name, locals(), RequestContext(request))


def show_category(request, category_slug, template_name="catalog/category.html"):
    featured = Product.featured.all()[:2]
    c = get_object_or_404(Category, slug=category_slug)
    products = c.product_set.all()
    page_title = c.name
    meta_keywords = c.meta_keywords
    meta_description = c.meta_description
    context = {
        'products': products,
        'page_title': page_title,
        'meta_keywords': meta_keywords,
        'meta_description': meta_description,
    }
    # context2 = RequestContext(request, context)
    request.session.set_test_cookie()
    return render(request, template_name, locals(), RequestContext(request))


@csrf_exempt
def show_product(request, product_slug, template_name="catalog/product.html"):
    p = get_object_or_404(Product, slug=product_slug)
    stats.log_product_view(request, p)
    product_reviews = ProductReview.approved.filter(product=p).order_by('-date')
    page = request.GET.get('page', 1)
    js = request.GET.get('js', '')
    paginator = Paginator(product_reviews, 1)
    reviews_count = product_reviews.count()
    try:
        product_reviews1 = paginator.page(page)
    except PageNotAnInteger:
        product_reviews1 = paginator.page(1)
    except EmptyPage:
        product_reviews1 = paginator.page(paginator.num_pages)
    if js == 'true':
        template = "catalog/product_review_paginated.html"
        html = render_to_string(template, {'product_reviews1': product_reviews1})
        response = simplejson.dumps({'success': 'True', 'html': html})
        return HttpResponse(response, content_type='application/javascript; charset=utf-8')

    if not product_reviews:
        review_form = ProductReviewForm()
    for r in product_reviews:
        print(request.user.username)
        print(r.user.username)
        if r.user.username == request.user.username:
            review_form = 'exists'
            print(review_form)
            break
        else:
            review_form = ProductReviewForm()
    print(review_form)
    categories = p.categories.filter(is_active=True)
    page_title = p.name
    meta_keywords = p.meta_keywords
    meta_description = p.meta_description
    # add to product view
    context = {
        'categories': categories,
        'page_title': page_title,
        'meta_keywords': meta_keywords,
        'meta_description': meta_description,
    }
    # need to evaluate the HTTP method
    if request.method == 'POST':
        if pending_checker(request) == 0:
            url = reverse('show_checkout', args=['PendingLipa'])
            return HttpResponseRedirect(url)
        # add to cart....create the bound form
        postdata = request.POST.copy()
        form = ProductAddToCartForm(request, postdata)
        # check if posted data is valid
        if form.is_valid():
            # add to cart and redirect to cart page
            cart.add_to_cart(request)
            # if test cookie worked, get rid of it
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            url = reverse('show_cart')
            return HttpResponseRedirect(url)
    else:
        # it's a get, create the unbound form. Note a request as a kwarg
        form = ProductAddToCartForm(request=request, label_suffix=':')
    # assign the hidden input the product slug
    form.fields['product_slug'].widget.attrs['value'] = product_slug
    # set the test cookie on our first get request
    request.session.set_test_cookie()
    return render(request, template_name, locals(), RequestContext(request))


@login_required
def add_review(request):
    form = ProductReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        slug = request.POST.get('slug')
        product = Product.active.get(slug=slug)
        review.user = request.user
        review.product = product
        print(review.user.username)
        review.save()
        template = "catalog/product_review.html"
        html = render_to_string(template, {'review': review})
        response = simplejson.dumps({'success': 'True', 'html': html})
    else:
        html = form.errors.as_ul()
        response = simplejson.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


@login_required
def add_tag(request):
    tags = request.POST.get('tag', '')
    slug = request.POST.get('slug', '')
    if len(tags) > 2:
        p = Product.active.get(slug=slug)
        html = u''
        template = "catalog/tag_link.html"
        for tag in tags.split():
            tag.strip(',')
        Tag.objects.add_tag(p, tag)
        for tag in p.tags:
            html += render_to_string(template, {'tag': tag})
        response = simplejson.dumps({'success': 'True', 'html': html})
    else:
        response = simplejson.dumps({'success': 'False'})
    return HttpResponse(response, content_type='application/javascript; charset=utf8')


def tag_cloud(request, template_name="catalog/tag_cloud.html"):
    product_tags = Tag.objects.cloud_for_model(Product, steps=9, distribution=tagging.utils.LOGARITHMIC, filters={ 'is_active': True })
    page_title = 'Product Tag Cloud'
    return render(request, template_name, locals(), RequestContext(request))


def tag(request, tag, template_name="catalog/tag.html"):
    products = TaggedItem.objects.get_by_model(Product.active, tag)
    return render(request, template_name, locals(), RequestContext(request))
