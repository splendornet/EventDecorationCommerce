from django.db import models
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')


class Admin_Header(models.Model):
    title = models.CharField(max_length=255, blank=True, verbose_name='title')
    is_active = models.BooleanField(default=True)
    sequence_number = models.IntegerField(blank=True,null=True)


    def __str__(self):
        return self.title


class Admin_HeaderMenu(models.Model):
    title_id = models.ForeignKey(Admin_Header, on_delete=models.CASCADE, verbose_name='title_id')
    sub_title = models.CharField(max_length=225, blank=True)
    menu_image = models.ImageField(upload_to='header_menu/', max_length=255,
                                   blank=True, null=True, default='image_not_found.jpg')
    def __str__(self):
        return self.sub_title


class Admin_HeaderSubMenu(models.Model):
    header_menu_id = models.ForeignKey(Admin_HeaderMenu, on_delete=models.CASCADE)
    sub_menu_title = models.CharField(max_length=225, blank=True)
    url = models.CharField(max_length=225, blank=True)
    menu_image = models.ImageField(upload_to='header_menu/',max_length=255,
        blank=True, null=True,default='image_not_found.jpg')

    def __str__(self):
        return self.sub_menu_title

class Manage_Menu(models.Model):
    header_menu = models.ForeignKey(Admin_Header, on_delete=models.CASCADE)
    offer_title =  models.CharField(max_length=225, blank=True)
    product = models.ManyToManyField(Product)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.offer_title

    def get_products_count(self):
        return ManageMenuMasterProducts.objects.filter(manage_menu= self.id, manage_product__is_deleted = False).count()


class ManageMenuMasterProducts(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    manage_menu = models.ForeignKey(
        Manage_Menu, blank=True, null=True,
        related_name='manage_menu', on_delete=models.CASCADE
    )
    manage_product = models.ForeignKey(
        Product, blank=True, null=True,
        related_name='manage_product', on_delete=models.CASCADE
    )

    def __str__(self):

        return str(self.date_created)

class ExhibitionOffers(models.Model):
    header_menu = models.ForeignKey(Admin_Header, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def get_products_count(self):
        return ExhibitionOffersCategory.objects.filter(manage_menu= self.id, manage_category__depth=1).count()


class ExhibitionOffersCategory(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    manage_menu = models.ForeignKey(
        ExhibitionOffers, blank=True, null=True,
        related_name='exhibition_menu', on_delete=models.CASCADE
    )
    manage_category = models.ForeignKey(
        Category, blank=True, null=True,
        related_name='manage_category', on_delete=models.CASCADE
    )

    def __str__(self):

        return str(self.date_created)


