from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from search import search
from ecomstore import settings
import json


# Create your views here.
def results(request, template_name="search/results.html"):
    # get current search phrase
    q = request.GET.get('q', '')
    # get current page number. Set to 1 is missing or invalid
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    # retrieve the matching products
    matching = search.products(q).get('products')
    # generate the pagintor object
    paginator = Paginator(matching, settings.PRODUCTS_PER_PAGE)
    try:
        results = paginator.page(page).object_list
    except (InvalidPage, EmptyPage):
        results = paginator.page(1).object_list
    # store the search
    search.store(request, q)
    # the usual...
    page_title = 'Search Results for: ' + q
    return render(request, template_name, locals(), RequestContext(request))


# This view returns a json response of data user types in the search box in realtime and displays suggestions
def autosearch(request):
    q = request.GET.get('q', '')
    data = list(search.products(q).get('products').values('name', 'description', 'sku', 'brand', 'meta_description',
                                                          'categories__name', 'categories__slug', 'meta_keywords',
                                                          'categories__description', 'categories__meta_keywords',
                                                          'categories__meta_description', 'slug', 'price', 'thumbnail',
                                                          'image_caption'))
    # loop through the items and check for redundant products.
    # Some products are redundant because they belong to more than one category.
    # note: This only works if redundant data follow the other immediately in the list
    data2 = []
    count = 0
    for d in data:
        # Check if the list data2 has any item in it. It should be empty in the first loop
        if len(data2) > 0:
            # if it has an item then check if the item we want to add in it shares a name with the existing one
            if len(data2) > 0 and d['name'] != data2[count]['name']:
                # if it does not then add the new item to the list and then increment count by 1
                data2.append(d)
                count += 1
        # if data2 list is empty. first time in the loop, just add the data but don't increment count.
        else:
            data2.append(d)

    testdata = data2.copy()
    # html = '<ul id="slist" class="sf" style="list-style: none;">'
    html = ''
    for p in testdata:
        html += '<li id="' + p['name'] + '" class="pitem"><img src="' + settings.MEDIA_URL + p['thumbnail'] + '" id="simage" /><label>' + p['name'] + '</label></li>'
    # html += '</ul>'
    print(html)

    data = data2
    return HttpResponse(html)
    # return JsonResponse(data, safe=False)


def removeDuplicate(data):
    seen = set()
    for x in data:
        t = tuple(x.items())
        if t not in seen:
            yield x
            seen.add(t)
