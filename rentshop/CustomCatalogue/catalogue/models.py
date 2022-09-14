# django imports
from django.db import models
from embed_video.fields import EmbedVideoField
# 3rd party imports
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductImage, AbstractCategory


class Category(AbstractCategory):

    """
    Category extended oscar model.
    """

    master_sequence = models.PositiveIntegerField(blank=True, null=True)
    show_on_frontside = models.BooleanField(default=True)
    image = models.FileField(upload_to='header_menu/category_img/', max_length=255,
                                   blank=True, null=True, default='image_not_found.jpg')
    icon = models.FileField(upload_to='header_menu/category_icon/', max_length=255,
                                   blank=True, null=True, default='image_not_found.jpg')
    show_in_icons = models.FileField(upload_to='header_menu/show_in_icon/', max_length=255,
                            blank=True, null=True, default='image_not_found.jpg')
    show_in = models.CharField(max_length=255, blank= True, null= True)
    sequence = models.IntegerField(blank= True, null= True)

    @property
    def get_precentage(self):
        perc = None

        id_list = [obj.id for obj in self.get_descendants_and_self() if obj.show_on_frontside]
        prod_perc = [product.get_perc for product in Product.objects.filter(is_deleted = False,is_approved = 'Approved',categories__in=id_list) if product.get_perc]
        if prod_perc:
            min_perc = min(prod_perc)
            max_perc = max(prod_perc)

            perc = '%s-%s' % (min_perc, max_perc)

            return perc
        return perc

class Product(AbstractProduct):

    """
    Product extended oscar model.
    """

    PRODUCT_COST_TYPE = (
        ('Single', 'Single'),
        ('Multiple', 'Multiple'),
    )

    is_approved = models.CharField(max_length=30, default='Pending')
    is_combo_product = models.BooleanField(default=False)
    daily_capacity = models.PositiveIntegerField(default = 1)
    is_deposite_applicable = models.BooleanField(default=False)
    deposite_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    is_transporation_available = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_quantity_allowed = models.BooleanField(default=True)
    rent_transportation_cost = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_transportation_cost = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    product_title_meta = models.CharField(max_length=255, blank=True, null=True)
    product_meta_data = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank= True, null= True)
    product_cost_type = models.CharField(max_length=255, default='Single', choices=PRODUCT_COST_TYPE)

    combo_start_date = models.DateTimeField(blank=True, null=True)
    combo_end_date = models.DateTimeField(blank=True, null=True)

    product_margin = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    product_tax_type = models.CharField(max_length=255, blank=True, null=True)

    product_booking_time_delay = models.IntegerField(blank=True, null=True, default=48)
    is_featured_product = models.BooleanField(default=False)
    is_artificial_flower = models.BooleanField(default=False)
    is_real_flower = models.BooleanField(default=False)
    youtube_video_link = models.CharField(max_length=256, blank=True, null=True)
    video = EmbedVideoField(blank= True, null= True)

    is_package = models.BooleanField(default=False)
    product_package = models.ManyToManyField("self", blank=True, symmetrical=False, null=True, related_name="package_product")

    @property
    def get_rate_card_count(self):
        count = 0
        if self.product_class.name == 'Rent Or Sale':
            for product in self.product_cost_entries.exclude(quantity_from__isnull=True, quantity_to__isnull=True,
                                                             rent_quantity_from__isnull=True,
                                                             rent_quantity_to__isnull=True):
                if product.quantity_from != None and product.quantity_to != None:
                    count = count + 1
                if product.rent_quantity_from != None and product.rent_quantity_to != None:
                    count = count + 1
        else:
            for product in self.product_cost_entries.exclude(quantity_from__isnull= True, quantity_to__isnull = True, rent_quantity_from__isnull = True ,rent_quantity_to__isnull = True):
                count = count + 1
        return count

    @property
    def get_display_cost_without_tax(self):

        stock = self.stockrecords.all().last()
        if stock:
            if self.product_class.name in ['Rent', 'Professional']:
                return stock.rent_price

            if self.product_class.name == 'Sale':
                return stock.price_excl_tax

            if self.product_class.name == 'Rent Or Sale':
                return str(stock.rent_price) + '/ ' + str(stock.price_excl_tax)

        return '-'

    @property
    def get_display_cost_without_tax_int(self):

        stock = self.stockrecords.all().last()
        if stock:
            if self.product_class.name in ['Rent', 'Professional']:
                return stock.rent_price

            if self.product_class.name == 'Sale':
                return stock.price_excl_tax

            if self.product_class.name == 'Rent Or Sale':
                return (stock.rent_price, stock.price_excl_tax)

        return 0

    @property
    def get_product_margin_cost(self):

        cost = self.get_display_cost_without_tax_int

        if isinstance(cost, type(())):

            cost_1, cost_2 = cost[0], cost[1]
            cost_1 = round(cost_1 * (self.product_margin / 100), 2)
            cost_2 = round(cost_2 * (self.product_margin / 100), 2)

            return str(cost_1) + '/ ' + str(cost_2)

        else:

            return round(cost * (self.product_margin / 100), 2)

    @property
    def get_display_cost(self):

        from CustomBasket.basket.templatetags.common import get_price_whole_int

        cost = get_price_whole_int(self.stockrecords.all().last())
        cost_without_tax = self.get_display_cost_without_tax_int

        if isinstance(cost, type(())):

            cost_1, cost_2 = cost[0], cost[1]
            cost_wt_1, cost_wt_2 = cost_without_tax[0], cost_without_tax[1]
            cost_1 = round(cost_1 + cost_wt_1 * (self.product_margin/100), 2)
            cost_2 = round(cost_2 + cost_wt_2 * (self.product_margin/100), 2)

            return str(cost_1) + '/ ' + str(cost_2)

        else:

            return round(cost + cost_without_tax * (self.product_margin/100), 2)

    @property
    def get_display_cost_filter(self):

        from CustomBasket.basket.templatetags.common import get_price_whole_int

        cost = get_price_whole_int(self.stockrecords.all().last())
        cost_without_tax = self.get_display_cost_without_tax_int

        if isinstance(cost, type(())):

            cost_1, cost_2 = cost[0], cost[1]
            cost_wt_1, cost_wt_2 = cost_without_tax[0], cost_without_tax[1]
            cost_1 = round(cost_1 + cost_wt_1 * (self.product_margin / 100), 2)
            cost_2 = round(cost_2 + cost_wt_2 * (self.product_margin / 100), 2)

            return round(cost_1)

        else:

            return round(cost + cost_without_tax * (self.product_margin / 100), 2)

    @property
    def get_cost_with_margin(self):

        cost = self.get_display_cost_without_tax_int

        if isinstance(cost, type(())):

            cost_1, cost_2 = cost[0], cost[1]
            cost_1 = round(cost_1 + cost_1 * (self.product_margin/100), 2)
            cost_2 = round(cost_2 + cost_2 * (self.product_margin/100), 2)

            return str(cost_1) + '/ ' + str(cost_2)

        else:

            return round(cost + cost * (self.product_margin/100), 2)


    @property
    def combo_validity_date(self):

        try:
            days = self.combo_end_date - self.combo_start_date
            return days.days
        except:
            return 'NA'

    @property
    def combo_price(self):
        try:
            record = self.stockrecords.all()
            return record.last().price_excl_tax
        except:
            return 'NA'

    @property
    def table_stock_record(self):
        try:
            count = 0
            for i in self.stockrecords.all():
                if i.num_in_stock is not None:
                    count = count + i.num_in_stock
                else:
                    count = 1
            return count
        except:
            return 1

    @property
    def table_vendor_name(self):

        name = ''

        try:
            for i in self.stockrecords.all():
                name = i.partner
        except Exception as e:
            pass

        return name

    def dp_image(self):

        """
        Method to return dp image.
        :return: image url.
        """

        images = self.get_all_images()
        if images:
            images = images.order_by('is_dp_image', 'img_sequence')

        try:
            images = images[0]
            return images
        except:
            return self.get_missing_image()

    def primary_image(self):

        """
        Oscar primary image extended method to get image by seq. number.
        :return: image url.
        """

        images = self.get_all_images()
        ordering = self.images.model.Meta.ordering
        if not ordering or ordering[0] != 'img_sequence':
            images = images.order_by('-is_dp_image', 'img_sequence')
        try:
            return images[0]
        except IndexError:
            return {
                'original': self.get_missing_image(),
                'caption': '',
                'is_missing': True
            }

    def get_all_images(self):

        """
        Oscar extended method to get product images by seq. number.
        :return: images list.
        """

        if self.is_child and not self.images.exists():
            return self.parent.images.all().order_by('-is_dp_image', 'img_sequence')
        return self.images.all().order_by('-is_dp_image', 'img_sequence')

    def __str__(self):

        return self.title


    @property
    def get_perc(self):
        try:

            record = self.stockrecords.all()
            price = record.last()

            if price.sale_price_with_tax and price.sale_round_off_price:
                sale_price = price.sale_price_with_tax + price.sale_round_off_price
            if price.sale_price_with_tax and not price.sale_round_off_price:
                sale_price = price.sale_price_with_tax
            if price.rent_price_with_tax and price.rent_round_off_price:
                rent_price = price.rent_price_with_tax + price.rent_round_off_price
            if price.rent_price_with_tax and not price.rent_round_off_price:
                rent_price = price.rent_price_with_tax

            if self.product_class.name == 'Sale':
                if price.sale_market_price > sale_price:
                    perc = ((price.sale_market_price - sale_price)/price.sale_market_price) * 100
                else:
                    perc = None
            else:
                if price.rent_market_price > rent_price:
                    perc = ((price.rent_market_price - rent_price) / price.rent_market_price) * 100
                else:
                    perc = None
            return round(perc,0)
        except Exception as e:
            return None


class ProductImage(AbstractProductImage):

    """
    Product image oscar extended.
    """

    img_sequence = models.PositiveIntegerField(null=True, blank=True)
    image_sequence = models.IntegerField(unique=True, null=True, blank=True)
    image_product_sequence = models.IntegerField(null=True, blank=True)
    is_dp_image = models.BooleanField(default=False)
    image_caption = models.TextField(max_length=1000, blank=True, null= True)

    class Meta:
        unique_together = ('image_product_sequence', 'product')


class ComboProducts(models.Model):

    """
    Product under combo products.
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    combo_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='combo_product')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='combo_child_product')
    product_title = models.CharField(max_length=255, blank=True, null=True)


class PremiumProducts(models.Model):

    """
    first 9 Products to show.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='premium_product_category')
    product = models.ManyToManyField(Product)

    def get_product_values(self):
        ret = ''
        # use models.ManyToMany field's all() method to return all the Department objects that this employee belongs to.
        for product in self.product.all():
            if not product.is_deleted:
                ret = ret + product.title + "("+product.upc+")"+','
        # remove the last ',' and return the value.
        return ret[:-1]


class ComboProductsMaster(models.Model):

    """
    Model to store combo products
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='combo_products', blank=True, null=True)

    vendor = models.ForeignKey('partner.Partner', on_delete=models.CASCADE, related_name='combo_vendor', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    upc = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)

    combo_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    round_combo_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    max_allowed = models.PositiveIntegerField(blank=True, null=True)

    combo_product = models.ManyToManyField(Product, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):

        return self.title


class ComboProductsMasterProducts(models.Model):

    """
    Model to store combo product
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    combo_offer = models.ForeignKey(ComboProductsMaster, blank=True, null=True, related_name='combo_offers', on_delete=models.CASCADE)
    combo_product = models.ForeignKey(Product, blank=True, null=True, related_name='cm_product', on_delete=models.CASCADE)

    def __str__(self):

        return str(self.date_created)


class ProductCostEntries(models.Model):

    """
    Model to store product cost entries
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_cost_entries')
    product_upc = models.CharField(max_length=255, blank=True, null=True)
    product_type = models.CharField(max_length=255, blank=True, null=True)

    vendor = models.ForeignKey('partner.Partner', on_delete=models.CASCADE, blank=True, null=True, related_name='vendor_product_cost_entries')

    quantity_from = models.PositiveIntegerField(blank=True, null=True)
    quantity_to = models.PositiveIntegerField(blank=True, null=True)
    requirement_day = models.PositiveIntegerField(blank=True, null=True)

    cost_incl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    transport_cost = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    rent_quantity_from = models.PositiveIntegerField(blank=True, null=True)
    rent_quantity_to = models.PositiveIntegerField(blank=True, null=True)
    rent_requirement_day = models.PositiveIntegerField(blank=True, null=True)

    rent_cost_incl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_transport_cost = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    is_transport = models.BooleanField(default=False)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    rent_remarks = models.CharField(max_length=255, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)



class Taxation(models.Model):

    TAX_APPLY_CHOICES = (
        ('1', 'For all rental products'),
        ('2', 'For all selling products'),
        ('3', 'For few products'),
        ('4', 'For all professional products'),

    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    # 15-01-2021: sale_tax_percent field add for rent or sale product class
    sale_tax_percent = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    apply_to = models.CharField(choices=TAX_APPLY_CHOICES, max_length=255,)
    products = models.ManyToManyField(Product, blank=True)

    def get_products(self):
        ret = ''

        for product in self.products.all():
            if not product.is_deleted:
                ret = ret + product.title + ','

        return ret[:-1]

class AdvancedPayPercentage(models.Model):

    PERCENTAGE_APPLY_CHOICES = (
        ('1', 'For all rental products'),
        ('2', 'For all selling products'),
        ('3', 'For all rent and sale products'),
        ('4', 'For all professional products'),

    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    advance_payment_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_advance_payment_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    apply_to = models.CharField(choices=PERCENTAGE_APPLY_CHOICES, max_length=255,)

    # def get_products(self):
    #     ret = ''
    #
    #     for product in self.products.all():
    #         ret = ret + product.title + ','
    #
    #     return ret[:-1]

class Attribute(models.Model):

    attribute = models.CharField(max_length = 255)
    value = models.CharField(max_length = 255,blank=True,null=True)


    def __str__(self):
        return self.attribute


class Attribute_Mapping(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='attribute_mapping')
    attribute = models.ForeignKey(Attribute,on_delete = models.CASCADE)
    value = models.CharField(max_length = 255)

class FilterValues(models.Model):

    filter_name = models.CharField(max_length = 255)

class CategoriesWiseFilterValue(models.Model):

    filter_name = models.ManyToManyField(FilterValues, blank=True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    filter_names = models.CharField(max_length = 400, null= True, blank= True)

class CategoriesWisePriceFilter(models.Model):

    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    from_value =  models.PositiveIntegerField(blank= True, null= True)
    to_value = models.PositiveIntegerField(blank= True, null= True)
    range = models.CharField(max_length= 100, blank= True, null= True)


from oscar.apps.catalogue.models import *  # noqa isort:skip
