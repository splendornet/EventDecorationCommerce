# python imports
import datetime
from decimal import Decimal

# django imports
from django import forms
from django.core.validators import RegexValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core import exceptions
from django.utils.translation import pgettext_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.forms.widgets import FileInput
from django_select2.forms import Select2Widget
from django.forms import inlineformset_factory,modelformset_factory, formset_factory

# 3rd party imports
from oscar.apps.dashboard.catalogue.forms import StockRecordForm, ProductForm, ProductCategoryForm
from oscar.forms.widgets import DatePickerInput, TimePickerInput
from oscar.apps.dashboard.reports.forms import ReportForm
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model
from treebeard.forms import movenodeform_factory
from oscar.forms.widgets import DateTimePickerInput, ImageInput
from oscar.apps.dashboard.catalogue.forms import ProductImageForm, ProductSearchForm
from oscar.apps.dashboard.ranges.forms import RangeForm
from oscar.apps.dashboard.vouchers.forms import VoucherForm, VoucherSetForm, VoucherSearchForm
from oscar.apps.dashboard.partners.forms import  PartnerSearchForm
from oscar.apps.dashboard.users.forms import UserSearchForm
from oscar.apps.dashboard.orders.forms import OrderSearchForm
from oscar.apps.dashboard.catalogue.forms import StockAlertSearchForm
from oscar.apps.dashboard.reviews.forms import DashboardProductReviewForm
# from ckeditor.widgets import CKEditorWidget
# internal imports

# models
Category = get_model('catalogue', 'Category')
ComboProductsMaster = get_model('catalogue', 'ComboProductsMaster')
ComboProducts = get_model('catalogue', 'ComboProducts')
Partner = get_model('partner', 'Partner')
VendorCalender = get_model('partner', 'VendorCalender')
StockRecord = get_model('partner', 'StockRecord')
ProductUnit = get_model('partner', 'ProductUnit')
Product = get_model('catalogue', 'Product')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductImage = get_model('catalogue', 'ProductImage')
Range = get_model('offer', 'Range')
Benefit = get_model('offer', 'Benefit')
Order = get_model('order', 'Order')
ProductReview = get_model('reviews', 'productreview')
User = get_user_model()
Attribute = get_model('catalogue', 'Attribute')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')
AdvancedPayPercentage = get_model('catalogue', 'AdvancedPayPercentage')
CategoriesWiseFilterValue = get_model('catalogue', 'CategoriesWiseFilterValue')
PriceRangeModel = get_model('offer', 'PriceRangeModel')
CouponDistributor = get_model('offer', 'CouponDistributor')
Voucher = get_model('voucher', 'Voucher')


# class
GeneratorRepository = get_class('dashboard.utils','GeneratorRepository')

# const.
product_status = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Disapproved', 'Disapproved')
)
PRODUCT_STATUS = (
    ('', 'Select type'),
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Disapproved', 'Disapproved')
)
PRODUCT_TYPE = (
    ('', 'Select type'),
    ('1', 'Sale'),
    ('2', 'Rent'),
    ('3', 'Rent Or Sale'),
    ('4', 'Service'),
    ('5', 'Professional'),
)
IS_IMAGE = (
    ('', 'Product has image'),
    ('1', 'Yes'),
    ('2', 'No'),
)

TAX_TYPE = (
    ('', 'Select tax type'),
    ('composition_tax', 'Composition Tax'),
    ('regular_tax', 'Regular Tax'),
)

# formset factory
CustomCategoryForm1 = movenodeform_factory(Category, fields=['name', 'description', 'image','icon', 'show_in','sequence','show_in_icons','show_on_frontside'])


class ComboSearchForm(forms.Form):

    """
    Combo offer search form
    """

    product_title = forms.CharField(required=False, max_length=100)
    upc = forms.CharField(required=False, max_length=100)
    status = forms.ChoiceField(required=False, choices=PRODUCT_STATUS)
    vendor_name = forms.CharField(label='ASP Name',required=False, max_length=100)


class CustomDashboardProductReviewForm(DashboardProductReviewForm):

    """
    Oscar extended product review update form.
    """

    choices = (
        (ProductReview.FOR_MODERATION, _('Requires moderation')),
        (ProductReview.APPROVED, _('Approved')),
        (ProductReview.REJECTED, _('Rejected')),
    )
    status = forms.ChoiceField(choices=choices, label=_("Status"), widget=Select2Widget)
    # body = forms.CharField(widget=CKEditorWidget(), required= False)

    class Meta:
        model = ProductReview
        fields = ('title', 'body', 'score', 'status')
        widgets = {
            'score' : Select2Widget,
        }


class CustomProductSearchForm(ProductSearchForm):

    """
    Oscar extended product search form.
    """

    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)

    status = forms.ChoiceField(required=False, choices=PRODUCT_STATUS)
    product_type = forms.ChoiceField(required=False, choices=PRODUCT_TYPE)
    is_image = forms.ChoiceField(required=False, choices=IS_IMAGE)
    vendor_name = forms.CharField(required=False, max_length=50, label='ASP name')
    vendor_pincode = forms.IntegerField(required=False,label = 'ASP Pincode')

    def clean(self):

        """
        Form clean method to validate form
        :return: validation
        """

        cleaned_data = super(CustomProductSearchForm, self).clean()
        cleaned_data['upc'] = cleaned_data['upc'].strip()
        cleaned_data['title'] = cleaned_data['title'].strip()
        cleaned_data['vendor_name'] = cleaned_data['vendor_name'].strip()
        return cleaned_data


class CustomProductCategoryForm(ProductCategoryForm):

    """
    Product category oscar extended form.
    """

    class Meta:

        model = ProductCategory
        fields = ('category',)
        ordering = ('-category')


class ComboProductCategoryForm(ProductCategoryForm):

    """
    Product category oscar extended form.
    """

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
    )

    class Meta:

        model = ProductCategory
        fields = ('category',)
        ordering = ('category')

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].initial=Category.objects.last()

class CustomStockRecordForm(StockRecordForm):

    """
    Product stock-record oscar extended form.
    """

    minimum_qty = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    tax_percentage = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    sale_tax_percentage = forms.DecimalField(min_value=0, decimal_places=2, required=False)

    rent_price = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    rent_price_with_tax = forms.DecimalField(min_value=0, decimal_places=2, required=False)

    sale_price_with_tax = forms.DecimalField(min_value=0, decimal_places=2, required=False)

    market_price = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    sale_market_price = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    rent_market_price = forms.DecimalField(min_value=0, decimal_places=2, required=False)

    total_saving = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    sale_total_saving = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    rent_total_saving = forms.DecimalField(min_value=0, decimal_places=2, required=False)

    round_off_price = forms.DecimalField(min_value=0, decimal_places=2, required=False, disabled=True)
    sale_round_off_price = forms.DecimalField(decimal_places=2, required=False)
    rent_round_off_price = forms.DecimalField(decimal_places=2, required=False)
    rent_transportation_price = forms.DecimalField(decimal_places=2, required=False)
    sale_transportation_price = forms.DecimalField(decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)

        self.fields['tax_percentage'].validators = [MinValueValidator(1), MaxValueValidator(100)]
        self.fields['price_excl_tax'].validators = [MinValueValidator(1)]
        self.fields['price_retail'].validators = [MinValueValidator(1)]
        self.fields['cost_price'].validators = [MinValueValidator(1)]
        self.fields['tax_percentage'].required = True
        self.fields['rent_price_with_tax'].widget.attrs['readonly'] = True
        self.fields['rent_round_off_price'].widget.attrs['readonly'] = True
        self.fields['sale_price_with_tax'].widget.attrs['readonly'] = True
        self.fields['sale_round_off_price'].widget.attrs['readonly'] = True
        self.fields['art_rent_price_with_tax'].widget.attrs['readonly'] = True
        self.fields['art_rent_round_off_price'].widget.attrs['readonly'] = True
        self.fields['art_sale_price_with_tax'].widget.attrs['readonly'] = True
        self.fields['art_sale_round_off_price'].widget.attrs['readonly'] = True
        self.fields['art_rent_total_saving'].widget.attrs['readonly'] = True
        self.fields['art_sale_total_saving'].widget.attrs['readonly'] = True

        if kwargs['product_class'].name == "Service":
            self.fields['partner'].required = False
            self.fields['tax_percentage'].required = False
            self.fields['partner_sku'].required = False
            self.fields['price_currency'].required = False

        if kwargs['product_class'].name == "Rent" or kwargs['product_class'].name == "Rent Or Sale":
            self.fields['advance_payment_percentage'].validators=[MinValueValidator(0), MaxValueValidator(100)]
            self.fields['advance_payment_percentage'].widget.attrs['value'] = 50
            self.fields['minimum_qty'].validators = [MinValueValidator(1)]
            self.fields['minimum_qty'].widget.attrs['value'] = 1
            self.fields['rent_price'].validators = [MinValueValidator(1)]

        if kwargs['product_class'].name == "Professional":
            self.fields['advance_payment_percentage'].validators = [MinValueValidator(0), MaxValueValidator(100)]
            self.fields['advance_payment_percentage'].widget.attrs['value'] = 100
            self.fields['minimum_qty'].validators = [MinValueValidator(1)]
            self.fields['minimum_qty'].widget.attrs['value'] = 1
            self.fields['minimum_qty'].widget.attrs['readonly'] = True
            self.fields['rent_price'].validators = [MinValueValidator(1)]

        if kwargs['product_class'].name == "Rent":
            adv_pay = AdvancedPayPercentage.objects.filter(apply_to = '1')
            if adv_pay:
                self.fields['advance_payment_percentage'].widget.attrs['value'] = adv_pay.last().advance_payment_percentage

        if kwargs['product_class'].name == "Sale":
            adv_pay = AdvancedPayPercentage.objects.filter(apply_to='2')
            if adv_pay:
                self.fields['advance_payment_percentage'].widget.attrs[
                    'value'] = adv_pay.last().advance_payment_percentage

        if kwargs['product_class'].name == "Rent Or Sale":
            adv_pay = AdvancedPayPercentage.objects.filter(apply_to='1')
            if adv_pay:
                self.fields['advance_payment_percentage'].widget.attrs[
                    'value'] = adv_pay.last().advance_payment_percentage
            sale_adv_pay = AdvancedPayPercentage.objects.filter(apply_to='2')
            if sale_adv_pay:
                self.fields['sale_advance_payment_percentage'].widget.attrs[
                    'value'] = sale_adv_pay.last().advance_payment_percentage

        if kwargs['product_class'].name == "Professional":
            adv_pay = AdvancedPayPercentage.objects.filter(apply_to='4')
            if adv_pay:
                self.fields['advance_payment_percentage'].widget.attrs[
                    'value'] = adv_pay.last().advance_payment_percentage


        self.fields['price_currency'].widget.attrs['readonly'] = True
        self.fields['rent_total_saving'].widget.attrs['readonly'] = True
        self.fields['sale_total_saving'].widget.attrs['readonly'] = True

        is_vendor = self.user.groups.filter(name='Vendor').exists()
        self.fields['partner_sku'].widget.attrs['readonly'] = True

        if is_vendor:
            self.fields['minimum_qty'].widget.attrs['readonly'] = True
            self.fields['advance_payment_percentage'].widget.attrs['readonly'] = True
            partner_obj = Partner.objects.get(users=self.user.id)
            self.fields['partner'].queryset = self.user.partners.filter(id=partner_obj.id)
            self.fields['partner'].initial = self.fields['partner'].queryset[0]
        else:
            active_user = User.objects.filter(is_active=True).values_list('id')
            active_partner = Partner.objects.filter(users__in=active_user)
            self.fields['partner'].queryset = active_partner

    class Meta:

        fields = [
            'partner', 'partner_sku',
            'price_currency', 'price_excl_tax', 'price_retail', 'cost_price',
            'num_in_stock', 'low_stock_threshold','minimum_qty','advance_payment_percentage','tax_percentage','shipping_charges',
            'rent_price', 'is_sale_and_rent', 'unit', 'sale_price_with_tax', 'rent_price_with_tax',
            'market_price', 'sale_market_price', 'rent_market_price', 'total_saving', 'sale_total_saving',
            'rent_total_saving', 'round_off_price', 'sale_round_off_price', 'rent_round_off_price','rent_transportation_price',
            'sale_transportation_price','sale_tax_percentage','sale_advance_payment_percentage',
            'art_rent_price','art_rent_price_with_tax','art_rent_total_saving','art_rent_round_off_price','art_rent_market_price',
            'art_sale_price','art_sale_price_with_tax','art_sale_total_saving','art_sale_round_off_price','art_sale_market_price',
        ]


class ComboProductSetForm(forms.ModelForm):

    """

    """

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)
        self.fields['product'].widget.attrs['class'] = 'combo_product_l'
        self.fields['product'].queryset = Product.objects.filter(is_combo_product=True, is_deleted=False)

    class Meta:
        model = ComboProducts
        fields = ['combo_product',]




class CustomProductImageForm(ProductImageForm):

    """
    Product image form oscar extended.
    """

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)

        self.fields['img_sequence'].widget.attrs['class'] = 'form-control seq-class is_vendor'
        self.fields['img_sequence'].widget.attrs['placeholder'] = 'Image sequence'
        self.fields['img_sequence'].label = ''

        self.fields['is_dp_image'].widget.attrs['class'] = 'is_dp_class is_vendor'
        self.fields['is_dp_image'].label = 'Product DP image'
        self.fields['caption'].widget.attrs['class'] = 'form-control seq-class is_vendor'
        self.fields['caption'].widget.attrs['placeholder'] = 'Image Caption'
        self.fields['caption'].label = ''
        self.fields['caption'].required = False

    class Meta:

        model = ProductImage
        fields = ['product', 'original', 'caption', 'img_sequence', 'is_dp_image','caption']

        widgets = {
            'original': ImageInput(),
            # 'caption': forms.HiddenInput(),
        }

    def save(self, *args, **kwargs):

        """
        Form save method.
        :param args: default
        :param kwargs: default
        :return: image form instance
        """

        kwargs['commit'] = False
        obj = super().save(*args, **kwargs)
        obj.display_order = self.get_display_order()
        obj.save()

        return obj

    def get_display_order(self):

        """
        Method to get display order seq.
        :return: display order seq.
        """

        return self.prefix.split('-').pop()



class ComboProductForm(ProductForm):

    """
    Combo product oscar extended form.
    """

    is_approved = forms.ChoiceField(choices=product_status, required=False)
    combo_start_date = forms.DateField(label=_("Offer from date"), required=True)
    combo_end_date = forms.DateField(label=_("Offer to date"), required=True)


    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['upc'].widget.attrs['class'] = 'form-control'
        self.fields['combo_start_date'].widget.attrs['class'] = 'form-control'
        self.fields['combo_end_date'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Product
        fields = [
            'title', 'upc', 'description', 'is_discountable',
            'structure', 'is_approved', 'combo_start_date', 'combo_end_date',
        ]
        widgets = {
            'structure': forms.HiddenInput(),
        }


class UPCMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.upc


class CustomProductForm(ProductForm):

    """
    Product model oscar extended form.
    """

    DAYS_BLOCKS = (
        (24, '1 Day'),
        (48, '2 Days'),
    )

    title = forms.CharField(min_length=2, max_length=500)
    is_approved = forms.ChoiceField(choices=product_status, required=False)
    upc = forms.CharField(min_length=2, max_length=50, validators = [RegexValidator('^([A-Za-z0-9])+$', message='Enter a valid UPC.')])
    is_combo_product = forms.BooleanField(required=False)
    is_transporation_available = forms.BooleanField(required=False)
    is_discountable = forms.BooleanField(required=False,initial=True)
    product_tax_type = forms.CharField(required=True, widget=forms.Select(choices=TAX_TYPE))
    meta_description = forms.CharField(required= False)
    # description = forms.CharField(widget=CKEditorWidget(), required= False)
    product_booking_time_delay = forms.ChoiceField(choices=DAYS_BLOCKS)

    # product_booking_time_delay = forms.IntegerField()
    product_package = UPCMultipleChoiceField(queryset=Product.objects.filter(is_approved='Approved', is_deleted=False))

    def __init__(self, *args, **kwargs):

        """
        ForProductFormClassm default init method.
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['product_title_meta'].widget.attrs['class'] = 'form-control'
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'
        self.fields['upc'].widget.attrs['class'] = 'form-control'
        self.fields['daily_capacity'].widget.attrs['class'] = 'form-control'
        self.fields['product_booking_time_delay'].widget.attrs['class'] = 'form-control'
        self.fields['youtube_video_link'].widget.attrs['class'] = 'form-control'
        self.fields['video'].widget.attrs['class'] = 'form-control'
        self.fields['deposite_amount'].widget.attrs['class'] = 'form-control'
        self.fields['daily_capacity'].required = False
        self.fields['youtube_video_link'].required = False
        self.fields['is_artificial_flower'].required = False
        self.fields['is_real_flower'].required = False
        prod_obj = Product.objects.filter(is_deleted = False,is_approved='Approved').exclude(product_class__name = 'Service')
        self.fields['product_package'].queryset = prod_obj
        self.fields['product_package'].required = False
        if self.instance.pk:
            prod_obj = Product.objects.filter(is_deleted=False, is_approved='Approved').exclude(
                product_class__name='Service').exclude(id= self.instance.pk)
            self.fields['product_package'].queryset = prod_obj

        if kwargs['product_class'].name == "Service":
            self.fields['product_booking_time_delay'].required = False

    class Meta:
        model = Product
        fields = [
            'title', 'upc', 'description', 'is_discountable',
            'structure', 'is_approved', 'is_combo_product','is_transporation_available','daily_capacity','is_deposite_applicable','deposite_amount',
            'product_cost_type', 'product_tax_type','is_quantity_allowed','product_title_meta','meta_description',
            'product_booking_time_delay','is_artificial_flower','is_real_flower','youtube_video_link','video','is_package','product_package',
        ]
        widgets = {
            'structure': forms.HiddenInput(),

        }

    def clean_daily_capacity(self):

        daily_capacity = self.cleaned_data.get('daily_capacity')

        if daily_capacity == 0:
            raise forms.ValidationError('Please enter valid daily capacity.')
        return self.cleaned_data.get('daily_capacity')

    def clean_upc(self):

        upc = self.cleaned_data.get('upc')

        if not upc:
            raise forms.ValidationError('Please enter upc.')
        if not self.instance.pk:
            obj = Product.objects.filter(upc__iexact = upc)
            if obj:
                raise forms.ValidationError('Product with this UPC already exists.')
        return self.cleaned_data.get('upc')



class ProductTypeUpdateForm(forms.ModelForm):

    """
    Product type update form.
    """

    class Meta:
        model = Product
        fields = ('product_class',)


class CustomReportForm(ReportForm):

    """
    Oscar extended report's form.
    """

    generators = GeneratorRepository().get_report_generators()

    type_choices = []
    for generator in generators:
        type_choices.append((generator.code, generator.description))

    report_type = forms.ChoiceField(
        widget=forms.Select(), choices=type_choices,
        label=_("Report Type"), help_text=_("Only the offer and order reports use the selected date range")
    )

    date_from = forms.DateField(label=_("Date from"), required=False, widget=DatePickerInput)
    date_to = forms.DateField(label=_("Date to"), help_text=_("The report is inclusive of this date"), required=False, widget=DatePickerInput)
    download = forms.BooleanField(label=_("Download"), required=False)

    def clean(self):

        """
        Clean method to validate form
        :return: validation.
        """

        date_from = self.cleaned_data.get('date_from', None)
        date_to = self.cleaned_data.get('date_to', None)
        if (all([date_from, date_to]) and self.cleaned_data['date_from'] > self.cleaned_data['date_to']):
            raise forms.ValidationError(_("Your start date must be before your end date"))
        return self.cleaned_data


class CustomRangeForm(RangeForm):

    """
    Offer range form oscar extended.
    """

    includes_all_products = forms.BooleanField(initial=True)
    # description = forms.CharField(widget=CKEditorWidget(), required= False)

    class Meta:
        model = Range
        fields = [
            'name', 'description', 'is_public',
            'includes_all_products', 'included_categories'
        ]
        exclude = ('included_categories',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(CustomRangeForm, self).__init__(*args, **kwargs)
        self.fields['includes_all_products'].widget = forms.HiddenInput()
        self.fields['includes_all_products'].required = False


class CustomVoucherForm(VoucherForm):

    """
    Oscar voucher form extended.
    """

    benefit_range = forms.ModelChoiceField(label=_('Which coupon session get a discount?'), queryset=Range.objects.all(),)

    type_choices = (
        (
            Benefit.PERCENTAGE, _('Percentage off of products in range')
        ),
    )

    benefit_type = forms.ChoiceField(choices=type_choices, label=_('Discount type'),)
    benefit_value = forms.DecimalField(max_value=100, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], label=_('Discount percentage'))
    exclusive = forms.BooleanField(required=False, label=_("Exclusive offers cannot be combined on the same items"))

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(CustomVoucherForm, self).__init__(*args, **kwargs)
        self.fields['exclusive'].widget = forms.HiddenInput()
        # self.fields['benefit_range'].required = False
        # self.fields['benefit_range'].widget = forms.HiddenInput()


class CustomVoucherSetForm(VoucherSetForm):

    """
    Voucher set form.
    """

    type_choices = (
        (Benefit.PERCENTAGE, _('Percentage off of products in range')),
    )


class CustomVoucherSearchForm(VoucherSearchForm):

    """
    Voucher search form oscar extended.
    """

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(CustomVoucherSearchForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].widget = forms.HiddenInput()
        self.fields['in_set'].widget = forms.HiddenInput()


class CustomPartnerSearchForm(PartnerSearchForm):

    """
    Vendor search form extended.
    """

    CHOICES = (('','Select'),('True', 'Active'), ('False', 'Inactive'),)
    _TYPE_CHOICES = (
        ('','Select type'),
        ('1', 'ASP Name'),
        ('2', 'ASP Email'),
        ('3', 'Business Name'),
        ('5', 'Phone Number'),
    )

    search_type = forms.ChoiceField(choices=_TYPE_CHOICES, required=False)
    all_search = forms.CharField(max_length=50, required=False, label='')
    pincode = forms.IntegerField(required=False, label='Pincode')
    status = forms.ChoiceField(choices=CHOICES, required=False ,label='Status')
    name = forms.CharField(widget=forms.HiddenInput(), required=False, label=pgettext_lazy(u"Partner's name", u"Name"))

class VendorCalendarAddEvent(forms.ModelForm):

    """
    Form to store vendor calendar.
    """
    from_date = forms.DateField(label=_("Date from"), required=True, widget=DatePickerInput)
    to_date = forms.DateField(label=_("Date from"), required=True, widget=DatePickerInput)

    class Meta:
        model = VendorCalender
        fields = ('product', 'from_date', 'to_date',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(VendorCalendarAddEvent, self).__init__(*args, **kwargs)

        user = User.objects.get(id=self.request.user.id)
        vendor = Partner.objects.filter(users=user).last()
        stock_record = StockRecord.objects.filter(partner=vendor)
        products = Product.objects.filter(id__in=stock_record.values_list('product', flat=True), is_deleted=False)

        self.fields['from_date'].widget.attrs['class'] = 'form-control'
        self.fields['to_date'].widget.attrs['class'] = 'form-control'
        self.fields['product'].queryset = products
        self.fields['product'].required = True

    def clean(self):

        """
        Form clean method.
        :return: validation
        """

        from_date = self.cleaned_data.get('from_date', None)
        to_date = self.cleaned_data.get('to_date', None)
        product = self.cleaned_data.get('product', None)

        if from_date:
            if from_date < datetime.datetime.now().date():
                raise forms.ValidationError('Please select current date.')

        if (all([from_date, to_date]) and self.cleaned_data['from_date'] > self.cleaned_data['to_date']):
            raise forms.ValidationError(_("Your start date must be before your end date"))

        if product and from_date and to_date:

            q1 = VendorCalender.objects.filter(
                product=product, to_date__gte=from_date
            ).exclude(id=self.instance.id)

            q2 = VendorCalender.objects.filter(
                product=product, from_date__range=[from_date, to_date]
            ).exclude(id=self.instance.id)

            q3 = VendorCalender.objects.filter(
                product=product, to_date__range=[from_date, to_date]
            ).exclude(id=self.instance.id)

            if q1 or q2 or q3:
                raise forms.ValidationError(
                    'Product already booked on that date range.'
                )

        return self.cleaned_data


class CustomUserSearchForm(UserSearchForm):

    """
    User extended search form.
    """
    STATUS_CHOICE = (
        ('', 'Select status'),
        ('True', 'Active'),
        ('False', 'Inactive'),
    )

    name = forms.CharField(min_length=1, required=False, label=pgettext_lazy(u"User's name", u"Name"))
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICE)


class ProductUnitModelForm(forms.ModelForm):

    """
    Model for to store unit.
    """

    unit = forms.CharField(max_length=60, required=True, validators = [RegexValidator('^([A-Za-z0-9_,/.%$@*&#!^()-`~+= ])+$', message='Enter a valid unit name.')])

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ProductUnitModelForm, self).__init__(*args, **kwargs)
        self.fields['unit'].widget.attrs['class'] = 'form-control'

    def clean_unit(self):

        """
        Form clean unit method to validate unit.
        :return: validation
        """

        if ProductUnit.objects.filter(unit=self.cleaned_data['unit']):
            raise forms.ValidationError('Unit with that name already exists.')
        return self.cleaned_data['unit']

    class Meta:
        model = ProductUnit
        fields = ('unit',)


class ProductUnitUpdateModelForm(forms.ModelForm):

    """
    Model for to store unit.
    """

    unit = forms.CharField(max_length=60, required=True, validators = [RegexValidator('^([A-Za-z_,/.%$@*&#!^()-`~+= ])+$', message='Enter a valid unit name.')])

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ProductUnitUpdateModelForm, self).__init__(*args, **kwargs)
        self.fields['unit'].widget.attrs['class'] = 'form-control'

    def clean_unit(self):

        """
        Form clean unit method to validate unit at updation.
        :return: validation.
        """

        if ProductUnit.objects.filter(unit=self.cleaned_data['unit']).exclude(pk=self.instance.pk):
            raise forms.ValidationError('Unit with that name already exists.')
        return self.cleaned_data['unit']

    class Meta:
        model = ProductUnit
        fields = ('unit',)


class ProductUnitSearchForm(forms.Form):

    """
    Form to search unit.
    """

    unit = forms.CharField(required=False)


class CustomProductReviewSearchForm(forms.Form):

    STATUS_CHOICES = (
                         ('', '------------'),
                     ) + ProductReview.STATUS_CHOICES


    MONTH_CHOICE = (
        ('', 'Select Month'),
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    )

    RATING_CHOICE = (
        ('', 'Select rating'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    )

    reviews = ProductReview.objects.all().order_by('-date_created').values_list('date_created', flat=True)
    YEAR_CHOICE = []
    YEAR_CHOICE.append(('', 'Select Year'),)
    for review in reviews:
        choice_tup = (review.year, review.year)
        if choice_tup not in YEAR_CHOICE:
            YEAR_CHOICE.append(choice_tup)
    title = forms.CharField(required=False, label=_("Title"))

    keyword = forms.CharField(required=False, label=_("Keyword"))
    date_from = forms.DateTimeField(required=False, label=_("Date from"))
    date_to = forms.DateTimeField(required=False, label=_('to'))
    name = forms.CharField(required=False, label=_('Customer name'))

    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label=_("Status"))
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.all(), label=_("Category"))
    date = forms.DateField(required=False, widget=DatePickerInput)
    month = forms.ChoiceField(required=False, choices=MONTH_CHOICE)
    year = forms.ChoiceField(required=False, choices=YEAR_CHOICE)
    rating = forms.ChoiceField(required=False, choices=RATING_CHOICE)

    def get_friendly_status(self):
        raw = int(self.cleaned_data['status'])
        for key, value in self.STATUS_CHOICES:
            if key == raw:
                return value
        return ''

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(CustomProductReviewSearchForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = forms.HiddenInput()
        self.fields['date_from'].widget = forms.HiddenInput()
        self.fields['date_to'].widget = forms.HiddenInput()
        self.fields['keyword'].widget = forms.HiddenInput()


class CustomStockAlertSearchForm(StockAlertSearchForm):

    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(is_deleted=False))

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(CustomStockAlertSearchForm, self).__init__(*args, **kwargs)

        self.fields['status'].widget = forms.HiddenInput()


class CustomOrderSearchForm(OrderSearchForm):

    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(is_deleted=False))
    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(CustomOrderSearchForm, self).__init__(*args, **kwargs)
        # self.fields['name'].widget = forms.HiddenInput()
        self.fields['product_title'].widget = forms.HiddenInput()
        self.fields['upc'].widget = forms.HiddenInput()
        self.fields['partner_sku'].widget = forms.HiddenInput()
        self.fields['date_from'].widget = forms.HiddenInput()
        self.fields['date_to'].widget = forms.HiddenInput()
        self.fields['voucher'].widget = forms.HiddenInput()
        self.fields['payment_method'].widget = forms.HiddenInput()
        self.fields['response_format'].widget = forms.HiddenInput()


class SeasonSearchForm(forms.Form):

    """
    Form to search coupon season
    """

    season_name = forms.CharField(required=False)


class VendorCalenderSearchForm(forms.Form):

    """
    Form to search vendor calendar.
    """

    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(is_deleted=False))
    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user")
        super(VendorCalenderSearchForm, self).__init__(*args, **kwargs)

        if self.user.is_superuser:
            query = Product.objects.filter(is_deleted= False)
        else:
            partner = Partner.objects.get(users=self.user)
            stockrecord = StockRecord.objects.filter(partner=partner).values_list('product', flat=True)
            query = Product.objects.filter(id__in=stockrecord,is_deleted=False)

        self.fields['product'] = forms.ModelChoiceField(required=False, queryset=query)


class VendorCalenderSearchForm1(forms.Form):

    """
    Form to search vendor calendar.
    """

    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(is_deleted = False))
    upc = forms.CharField(required=False, label=_("UPC"))
    vendor = forms.ModelChoiceField(required=False, queryset=Partner.objects.all())
    date = forms.DateField(required=False, widget=DatePickerInput)


class ComboProductsMasterModelForm(forms.ModelForm):

    title = forms.CharField(max_length=200, required=True)
    combo_price = forms.DecimalField(required=True)

    class Meta:
        model = ComboProductsMaster
        fields = ('product', 'title', 'description', 'combo_price', 'combo_product', 'is_active')

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        # for combo product
        self_product_q = None
        self_product = kwargs.pop('self_product')
        if self_product:
            self_product_q = Product.objects.filter(id=self_product,is_deleted=False)

        # user
        product_user = kwargs.pop('product_user')

        super(ComboProductsMasterModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['placeholder'] = 'Combo Offer Title'

        self.fields['description'].widget.attrs['class'] = 'form-control'

        self.fields['combo_price'].widget.attrs['class'] = 'form-control'
        self.fields['combo_price'].widget.attrs['placeholder'] = 'Combo Offer Price'

        self.fields['combo_product'].widget.attrs['class'] = 'form-control'

        # for vendor
        product_set = Product.objects.filter(is_approved='Approved', product_class__name__in=['Rent', 'Sale', 'Rent Or Sale'],is_deleted=False)

        if self_product_q:
            product_set = product_set.exclude(id__in=self_product_q.values_list('id', flat=True))

        if product_user.is_staff and not product_user.is_superuser:

            vendor_user = Partner.objects.get(users=product_user)
            vendor_stock = StockRecord.objects.filter(partner=vendor_user).values_list('product', flat=True)

            product_set = product_set.filter(id__in=vendor_stock)

        self.fields['combo_product'].queryset = product_set
        self.fields['product'].queryset = Product.objects.filter(id=self_product,is_deleted=False)
        self.initial['product'] = Product.objects.get(id=self_product)


class CustomAttributeForm(forms.ModelForm):
    distinct_attribute = Attribute.objects.distinct('attribute')
    attribute = forms.ModelChoiceField(label="",
                                       queryset=Attribute.objects.filter(id__in=distinct_attribute.values('id')),
                                       empty_label="Select Attribute",
                                       widget=forms.Select(attrs={
                                           'onchange': 'get_attributechange1();'
                                                }
                                            )
                                       )
    VALUE_CHOICES = []
    for att in Attribute.objects.distinct('value'):
        VALUE_CHOICES.append((att.value, att.value))
    value = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """
        super(CustomAttributeForm, self).__init__(*args, **kwargs)
        self.fields['attribute'].widget.attrs['class'] = 'form-attribute-control'
        self.fields['value'].widget.attrs['class'] = 'form-values-control'
        self.fields['attribute'].required = False
        self.fields['value'].required = False

        VALUE_CHOICES = []
        for att in Attribute.objects.distinct('value'):
            VALUE_CHOICES.append((att.value, att.value))
        self.fields['value'].choices = VALUE_CHOICES
        if self.instance.pk:
            self.fields['value'].choices = VALUE_CHOICES

    class Meta:

        model = Attribute_Mapping
        fields = ['product', 'attribute', 'value']

class CustomAuthenticationForm(AuthenticationForm):

    def clean(self):
        _status = 0
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:

            try:

                _user = User.objects.get(email=username)

                if _user.is_staff:
                    if not _user.is_active:
                        _status = 4
                else:

                    if not _user.is_active and not _user.profile_user.is_blocked:
                        _status = 1
                    elif not _user.is_active and _user.profile_user.is_blocked:
                        _status = 2
                    else:
                        print('#01')


            except Exception as e:
                pass

            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:

                if _status == 0:
                    raise forms.ValidationError(' Please enter a correct username and password. Note that both fields may be case-sensitive.')
                elif _status == 1:
                    raise forms.ValidationError('Please activate your account, we have sent you activation link on your registered email id.')
                elif _status == 2:
                    raise forms.ValidationError('Account is disabled. Please contact admin.')
                elif _status == 4:
                    raise forms.ValidationError('Account is disabled. Please contact admin.')
                else:
                    raise forms.ValidationError('Please enter valid username or password')

            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

from django.forms.widgets import ClearableFileInput
class MyClearableFileInput(ClearableFileInput):
    initial_text = 'currently'
    input_text = 'change'
    clear_checkbox_label = ''

from django.forms.widgets import ClearableFileInput
class MyClearableFileInput1(ClearableFileInput):
    initial_text = ''
    input_text = ''
    clear_checkbox_label = ''

def validate_image_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Please upload only .jpg, jpeg , .svg or .png image.')


class CustomCategoryForm(CustomCategoryForm1):


    SHOW_IN_CHOICES = (
        ('0', 'Select Option'),
        ('1', 'Best Deals'),
        ('2', 'What We Offer'),
    )

    show_in = forms.ChoiceField(choices= SHOW_IN_CHOICES, required= False)
    sequence = forms.IntegerField(min_value= 1)
    image = forms.FileField(widget= MyClearableFileInput , required= False, validators=[validate_image_extension])
    icon = forms.FileField(widget= MyClearableFileInput, required= False, validators=[validate_image_extension], label=_("Rental catalogue icon"))
    # show_in_icons = forms.FileField(widget= MyClearableFileInput, required= False, validators=[validate_image_extension])
    show_in_icons = forms.FileField(widget= FileInput, required=False,validators=[validate_image_extension], label=_("What we offers icon"))
    # description = forms.CharField(widget=CKEditorWidget(), required= False)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """
        super(CustomCategoryForm, self).__init__(*args, **kwargs)
        self.fields['show_in'].widget.attrs['class'] = 'form-control'
        self.fields['sequence'].widget.attrs['class'] = 'form-control'
        self.fields['sequence'].widget.attrs['class'] = 'form-control'
        self.fields['sequence'].widget.attrs['class'] = 'form-control'
        self.fields['sequence'].required = False
        # self.fields['image'].widget = MyClearableFileInput


    def clean(self):
        show_in = self.cleaned_data.get('show_in')
        sequence = self.cleaned_data.get('sequence')

        if show_in and sequence != None:
            if self.instance.pk:
                cat_obj = Category.objects.filter(show_in = show_in, sequence = sequence).exclude(id= self.instance.pk)
            else:
                cat_obj = Category.objects.filter(show_in=show_in, sequence=sequence)
            if cat_obj:
                raise forms.ValidationError("Already allocated that sequence to other category")



        return self.cleaned_data

class CustomRangeForm1(RangeForm):

    """
    Offer range form oscar extended.
    """

    includes_all_products = forms.BooleanField(initial=False)
    # description = forms.CharField(widget=CKEditorWidget(), required= False)
    min_billing_amount = forms.DecimalField(decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], required=False)

    class Meta:
        model = Range
        fields = [
            'name', 'is_public','description','min_billing_amount',
            'includes_all_products', 'included_categories',
        ]
        # exclude = ('included_categories',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(CustomRangeForm1, self).__init__(*args, **kwargs)
        self.fields['includes_all_products'].widget = forms.HiddenInput()
        self.fields['includes_all_products'].required = False
        self.fields['name'].required = False
        self.fields['name'].widget = forms.HiddenInput()
        self.fields['is_public'].widget = forms.HiddenInput()
        self.fields['description'].label = "Terms and Condition"
        self.fields['min_billing_amount'].label = "Applicable for min billing amount"


class CustomVoucherForm1(VoucherForm):

    """
    Oscar voucher form extended.
    """

    benefit_range = forms.ModelChoiceField(label=_('Which coupon session get a discount?'), queryset=Range.objects.all(),)

    type_choices = (
        (
            Benefit.PERCENTAGE, _('Percentage off of products in range')
        ),
        (
            Benefit.FIXED, _('Amount off of products in range')
        ),
        # (
        #     Benefit.CUSTOMIZE_BENEFIT, _('customize coupon range')
        # ),
    )

    benefit_type = forms.ChoiceField(choices=type_choices, label=_('Discount type'),)
    benefit_value = forms.DecimalField(decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], label=_('Discount'))
    exclusive = forms.BooleanField(required=False, label=_("Exclusive offers cannot be combined on the same items"))

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(CustomVoucherForm1, self).__init__(*args, **kwargs)
        self.fields['exclusive'].widget = forms.HiddenInput()
        self.fields['benefit_range'].required = False
        self.fields['benefit_range'].widget = forms.HiddenInput()

    def clean_discount(self):
        discount = self.cleaned_data.get('benefit_value')
        discount_type = self.cleaned_data.get('benefit_type')
        if discount < 0:
            raise forms.ValidationError('Discount cannot be negative')
        if discount_type and discount_type == 'Percentage':
            if discount > 100:
                raise forms.ValidationError('Discount percentage cannot be greater than 100')
        return discount
