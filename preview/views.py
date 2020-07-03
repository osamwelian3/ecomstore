from django.shortcuts import render, reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from catalog.models import Product
from .forms import ProductCreationForm
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render_to_response("index.html", locals())


@login_required
def uploadproduct(request, template_name="test_upload.html"):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('homalog'))
    form = ProductCreationForm()
    if request.method == "POST":
        postdata = request.POST.copy()
        images = request.FILES
        form = ProductCreationForm(postdata, images)
        if form.is_valid():
            form.save()
            url = reverse('upload')
            return HttpResponseRedirect(url)
    page_title = 'Upload Product'
    return render(request, template_name, locals())
