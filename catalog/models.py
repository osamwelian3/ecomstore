from django.db import models
from django.urls import reverse
import os
from ecomstore import settings
from django.contrib.auth.models import User
import tagging.registry as tagging
# from . import views

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, help_text='Unique value for product page URL, created from name.')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    meta_keywords = models.CharField("Meta Keywords", max_length=255, help_text='Comma-delimited set ofSEO keywords for meta tag')
    meta_description = models.CharField("Meta Description", max_length=255, help_text='Content for description meta tag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        ordering = ['-created_at']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog_category', args=[str(self.slug)])

    """def get_absolute_url(self):
        return reverse('catalog_category', {'category_slug': self.slug})"""


def image_name(instance, filename):
    ext = filename.split('.')[-1]
    pid = Product.objects.all().count() + 1
    try:
        id = Product.objects.latest('created_at').id + 1
    except Exception:
        id = 1
    if Product.objects.filter(id=instance.id):
        p = Product.objects.get(id=instance.id)
        pimage = p.image.url
        pid = pimage.rsplit('_', 1)[1].rsplit('.', 1)[0]
        id = instance.id
    filename = "%s_%s_%s.%s" % (instance.slug, id, pid, ext)
    fullname = os.path.join(settings.MEDIA_ROOT + 'images/products/main', filename)
    print(fullname)
    if os.path.exists(fullname):
        os.remove(fullname)
    return os.path.join('images/products/main', filename)


def thumbnail_name(instance, filename):
    ext = filename.split('.')[-1]
    pid = Product.objects.all().count() + 1
    try:
        id = Product.objects.latest('created_at').id + 1
    except Exception:
        id = 1
    if Product.objects.filter(id=instance.id):
        p = Product.objects.get(id=instance.id)
        pimage = p.thumbnail.url
        pid = pimage.rsplit('_', 1)[1].rsplit('.', 1)[0]
        id = instance.id
    filename = "%s_%s_%s.%s" % (instance.slug, id, pid, ext)
    fullname = os.path.join(settings.MEDIA_ROOT + 'images/products/thumbnails', filename)
    print(fullname)
    if os.path.exists(fullname):
        os.remove(fullname)
    return os.path.join('images/products/thumbnails', filename)


class FeaturedProductManager(models.Manager):
    def all(self):
        return super(FeaturedProductManager, self).all().filter(is_active=True).filter(is_featured=True)


class ActiveProductManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProductManager, self).get_query_set().filter(is_active=True)


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, help_text='Unique value for product page URL, created from name.')
    brand = models.CharField(max_length=50)
    sku = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    old_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, default=0.00)
    image = models.ImageField(upload_to=image_name)
    thumbnail = models.ImageField(upload_to=thumbnail_name)
    image_caption = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    quantity = models.IntegerField()
    description = models.TextField()
    meta_keywords = models.CharField(max_length=255, help_text='Comma-delimited set of SEO keywords for meta tag')
    meta_description = models.CharField(max_length=255, help_text='Content for description meta tag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)

    objects = models.Manager()
    active = ActiveProductManager()
    featured = FeaturedProductManager()

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog_product', args=[str(self.slug)])

    """def get_absolute_url(self):
        return reverse('catalog_product', (), {'product_slug': self.slug})"""

    @property
    def category(self):
        return self.categories

    @property
    def sale_price(self):
        if self.old_price > self.price:
            return self.price
        else:
            return None

    def cross_sells(self):
        from checkout.models import Order, OrderItem
        orders = Order.objects.filter(orderitem__product=self)
        order_items = OrderItem.objects.filter(order__in=orders).exclude(product=self)
        products = Product.active.filter(orderitem__in=order_items).distinct()
        return products

    def cross_sells_user(self):
        from checkout.models import Order, OrderItem
        from django.contrib.auth.models import User
        users = User.objects.filter(order__orderitem__product=self)
        items = OrderItem.objects.filter(order__user__in=users).exclude(product=self)
        products = Product.active.filter(orderitem__in=items).distinct()
        return products

    def cross_sells_hybrid(self):
        from checkout.models import Order, OrderItem
        from django.contrib.auth.models import User
        from django.db.models import Q
        orders = Order.objects.filter(orderitem__product=self)
        users = User.objects.filter(order__orderitem__product=self)
        items = OrderItem.objects.filter(Q(order__in=orders) |
                                         Q(order__user__in=users)
                                         ).exclude(product=self)
        products = Product.active.filter(orderitem__in=items).distinct()
        return products


try:
    tagging.register(Product)
except tagging.AlreadyRegistered:
    pass


class ActiveProductReviewManager(models.Manager):
    def all(self):
        return super(ActiveProductReviewManager, self).all().filter(is_approved=True)


class ProductReview(models.Model):
    RATINGS = ((5, 5), (4, 4), (3, 3), (2, 2), (1, 1),)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(default=5, choices=RATINGS)
    is_approved = models.BooleanField(default=True)
    content = models.TextField()

    objects = models.Manager()
    approved = ActiveProductReviewManager()

    def __str__(self):
        return '"' + self.title + '" for ' + self.product.name
