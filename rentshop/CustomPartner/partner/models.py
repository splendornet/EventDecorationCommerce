# django imports
from django.db import models

# 3rd party imports
from oscar.apps.partner.abstract_models import AbstractPartner, AbstractStockRecord, AbstractStockAlert
from oscar.core.loading import get_model
from oscar.core.compat import get_user_model

# internal imports

State = get_model('country', 'State')
City = get_model('country', 'City')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')

User = get_user_model()


class Partner(AbstractPartner):

    """
    Oscar extended model to store vendor/partner.
    """

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    pan_number = models.CharField(max_length=12,blank=True, null=True)
    vat_number = models.CharField(max_length=12,blank=True, null=True)
    shop_act_number = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=255, blank=True, null=True)
    aadhar_number = models.CharField(max_length=255, blank=True, null=True)

    telephone_number = models.CharField(max_length=20, blank=True, null=True)
    alternate_mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email_id = models.EmailField(null=True, default=None)

    address_line_1 = models.CharField(max_length=100,blank=True, null=True)
    address_line_2 = models.CharField(max_length=100,blank=True, null=True)
    country = models.CharField(max_length=100,blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='State', blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='City', blank=True)
    pincode = models.CharField(max_length=10,blank=True, null=True)

    categories = models.CharField(max_length=100,blank=True, null=True)

    business_name = models.CharField(max_length=101,blank=True, null=True)
    bank_name = models.CharField(max_length=100,blank=True, null=True)
    account_holder_name = models.CharField(max_length=100,blank=True, null=True)
    account_number = models.CharField(max_length=100,blank=True, null=True)
    ifsc_code = models.CharField(max_length=20,blank=True, null=True)

    updated_date = models.DateTimeField(blank=True, null=True)

    digital_signature = models.ImageField(blank=True, null=True, upload_to='vendor_digital_signature/')

    class META:
        permissions = (('dashboard_access', 'can access dashboard'), )

    @property
    def vendor_full_address(self):

        """
        Method property to return vendor full address
        :return: address
        """

        try:

            address = '%s, %s, %s, %s - %s' %(self.address_line_1, self.address_line_2, self.city, self.state, str(self.pincode))
            return address

        except:

            return '-'

    @property
    def vendor_full_address_list(self):

        """
        Method property to return vendor full address
        :return: address
        """

        try:

            address = [self.address_line_1 + ', ' +self.address_line_2, self.city, self.state, str(self.pincode)]
            return address

        except:

            return None

    @property
    def vendor_status(self):

        """
        Method property to return vendor status.
        :return: status (1/0)
        """

        status = '-'

        try:
            for user in self.users.all():
                if user.is_active:
                    status = 'Active'
                else:
                    status = 'Inactive'

        except:
            pass

        return status


class StockRecord(AbstractStockRecord):

    """
    Oscar extended model to store product stock-record vendor wise.
    """

    advance_payment_percentage = models.DecimalField(decimal_places= 2, max_digits=12, null= True, blank=True)
    sale_advance_payment_percentage = models.DecimalField(decimal_places= 2, max_digits=12, null= True, blank=True)
    minimum_qty = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    tax_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_tax_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    shipping_charges = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    sale_price_with_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    rent_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_price_with_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    # updated price fields
    market_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_market_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_market_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    total_saving = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_total_saving = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_total_saving = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    round_off_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_round_off_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_round_off_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    is_sale_and_rent = models.BooleanField(default=False, blank=True)
    unit = models.ForeignKey('partner.ProductUnit', on_delete=models.SET_NULL, blank=True, null=True)

    rent_transportation_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    sale_transportation_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    # new field for artificial flower price
    art_rent_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_rent_price_with_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_rent_total_saving = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_rent_round_off_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_rent_market_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_rent_transportation_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    art_sale_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_sale_price_with_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_sale_total_saving = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_sale_round_off_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_sale_market_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    art_sale_transportation_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    @property
    def sale_base_price(self):
        sale_price = 0
        arti_sale_price = 0
        try:
            if self.product.is_real_flower and not self.product.is_artificial_flower:
                sale_price = 0
            else:
                if self.sale_price_with_tax and self.sale_round_off_price:
                    sale_price = self.sale_price_with_tax + self.sale_round_off_price
                if self.sale_price_with_tax and not self.sale_round_off_price:
                    sale_price = round(self.sale_price_with_tax)
                if not self.sale_price_with_tax and self.price_excl_tax:
                    sale_price = round(self.price_excl_tax)

            if self.product.is_real_flower:
                if self.art_sale_price_with_tax and self.art_sale_round_off_price:
                    arti_sale_price = self.art_sale_price_with_tax + self.art_sale_round_off_price
                if self.art_sale_price_with_tax and not self.art_sale_round_off_price:
                    arti_sale_price = round(self.art_sale_price_with_tax)
                if not self.art_sale_price_with_tax and self.price_excl_tax:
                    arti_sale_price = round(self.art_sale_price)

            if sale_price > 0 and arti_sale_price > 0:
                final_price = min(sale_price, arti_sale_price)
            elif sale_price > 0:
                final_price = sale_price
            elif arti_sale_price > 0:
                final_price = arti_sale_price
            else:
                final_price = 0

            return '{:,.2f}'.format(final_price)
        except Exception as e:
            print(e.args)
        return 0

    @property
    def rent_base_price(self):
        rentprice = 0
        arti_rent_price = 0
        try:
            if self.product.is_real_flower and not self.product.is_artificial_flower:
                rentprice = 0
            else:
                if self.rent_price_with_tax and self.rent_round_off_price:
                    rentprice = self.rent_price_with_tax + self.rent_round_off_price
                if self.rent_price_with_tax and not self.rent_round_off_price:
                    rentprice = round(self.rent_price_with_tax)
                if not self.rent_price_with_tax and self.rent_price:
                    rentprice = round(self.rent_price)

            if self.product.is_real_flower:
                if self.art_rent_price_with_tax and self.art_rent_round_off_price:
                    arti_rent_price = self.art_rent_price_with_tax + self.art_rent_round_off_price
                if self.art_rent_price_with_tax and not self.art_rent_round_off_price:
                    arti_rent_price = round(self.art_rent_price_with_tax)
                if not self.art_rent_price_with_tax and self.art_rent_price:
                    arti_rent_price = round(self.art_rent_price)

            if rentprice > 0 and arti_rent_price > 0:
                final_price = min(rentprice, arti_rent_price)
            elif rentprice > 0:
                final_price = rentprice
            elif arti_rent_price > 0:
                final_price = arti_rent_price
            else:
                final_price = 0
            return '{:,.2f}'.format(final_price)
        except Exception as e:
            print(e.args)
        return 0

    @property
    def sale_float_price(self):
        price = self.sale_base_price
        if ',' in str(price):
            price = float(str(price).replace(',', ''))
        else:
            price = float(price)
        return price

    @property
    def rent_float_price(self):
        price = self.rent_base_price
        if ',' in str(price):
            price = float(str(price).replace(',', ''))
        else:
            price = float(price)
        return price


class ProductUnit(models.Model):

    """
    Model to store product units
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    unit = models.CharField(max_length=255)

    def __str__(self):
        return self.unit


class VendorCalender(models.Model):

    """
    Model to store vendor bookings.
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    vendor = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='vendor_calender')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='vendor_calender_product', blank=True, null=True)

    from_date = models.DateTimeField()
    to_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):

        return str(self.from_date)


class MultiDB(models.Model):

    """
    Model to fronlinear and backup vendors
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='backup_category')
    frontliener = models.ManyToManyField(Partner, related_name='Backup_frontliener',verbose_name="Frontliner")
    backup1 = models.ManyToManyField(Partner, related_name='backup1')
    backup2 = models.ManyToManyField(Partner, related_name='backup2')

    def get_frontliener_values(self):
        ret = ''
        for frontliener in self.frontliener.all():
            ret = ret + frontliener.name + ','
        return ret[:-1]

    def get_backup1_values(self):
        ret = ''
        for backup1 in self.backup1.all():
            ret = ret + backup1.name + ','
        return ret[:-1]

    def get_backup2_values(self):
        ret = ''
        for backup2 in self.backup2.all():
            ret = ret + backup2.name + ','
        return ret[:-1]


class IndividualDB(models.Model):

    """
    Model to fronlinear and backup vendors
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='individual_category')
    individual_asp = models.ManyToManyField(Partner, related_name='individual_asp')

    def get_individual_asp_values(self):
        ret = ''
        for individual_asp in self.individual_asp.all():
            ret = ret + individual_asp.name + ','
        return ret[:-1]

class VendorProductStatus(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    vendor = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='vendors_name',blank=True)
    product_status = models.TextField(blank=True, null=True)



from oscar.apps.partner.models import *
