# django imports
from django import forms
from django.forms import formset_factory
from django.forms.models import modelform_factory, inlineformset_factory
# from ckeditor.widgets import CKEditorWidget

# package import
from oscar.core.loading import get_class, get_model

# internal imports
Product = get_model('catalogue', 'Product')
ComboProductsMaster = get_model('catalogue', 'ComboProductsMaster')
ComboProductsMasterProducts = get_model('catalogue', 'ComboProductsMasterProducts')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')


PRODUCT_STATUS = (
    ('', 'Select type'),
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Disapproved', 'Disapproved')
)

ACTIVE_STATUS = (
    ('', 'Status'),
    ('1', 'Active'),
    ('0', 'Inactive'),
)


class ComboSearchForm(forms.Form):

    """
    Form to search combo offers
    """

    product_title = forms.CharField(required=False, max_length=100)
    offer_title = forms.CharField(required=False, max_length=100)
    upc = forms.CharField(required=False, max_length=100)
    status = forms.ChoiceField(choices=ACTIVE_STATUS, required=False)
    vendor_name = forms.CharField(label="ASP name", max_length=100, required=False)


class ComboProductsMasterProductsModelForm(forms.ModelForm):

    """
    Product model form
    """

    class Meta:
        model = ComboProductsMasterProducts
        fields = ('combo_offer', 'combo_product',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        product_user = kwargs.pop('product_user')

        qs = Product.objects.filter(is_combo_product=True, is_approved='Approved',is_deleted=False)

        vendor = Partner.objects.filter(users=product_user)

        if product_user.is_staff and not product_user.is_superuser and vendor:

            stock = StockRecord.objects.filter(partner=vendor.last()).values_list('product', flat=True)
            qs = qs.filter(id__in=stock)

        super(ComboProductsMasterProductsModelForm, self).__init__(*args, **kwargs)
        self.fields['combo_product'].widget.attrs['class'] = 'cm-product'
        self.fields['combo_product'].queryset = qs


ComboFormsetExtra = inlineformset_factory(
    ComboProductsMaster, ComboProductsMasterProducts, ComboProductsMasterProductsModelForm,
    extra=10, max_num=10
)


class ComboProductsMasterV1ModelForm(forms.ModelForm):

    title = forms.CharField(max_length=200, required=True)
    combo_price = forms.DecimalField(required=True)
    # description = forms.CharField(widget=CKEditorWidget(), required= False)


    class Meta:
        model = ComboProductsMaster
        fields = (
            'product', 'title', 'description', 'upc',
            'combo_price', 'is_active', 'max_allowed',
        )

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ComboProductsMasterV1ModelForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['placeholder'] = 'Combo Offer Title'
        self.fields['combo_price'].widget.attrs['class'] = 'form-control'
        self.fields['upc'].widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = 'form-checkbox'
        self.fields['max_allowed'].widget.attrs['class'] = 'form-control'
        self.fields['max_allowed'].widget.attrs['placeholder'] = 'Combo Offer Max Allotment'
        self.fields['max_allowed'].required = False
        self.fields['combo_price'].widget.attrs['placeholder'] = 'Combo Offer Price'

    def clean_upc(self):

        if self.cleaned_data.get('upc'):
            if self.instance:
                if ComboProductsMaster.objects.filter(upc=self.cleaned_data.get('upc')).exclude(id=self.instance.id) or Product.objects.filter(upc=self.cleaned_data.get('upc')):
                    raise forms.ValidationError('UPC is already exists.')
            else:
                if ComboProductsMaster.objects.filter(upc=self.cleaned_data.get('upc')) or Product.objects.filter(upc=self.cleaned_data.get('upc')):
                    raise forms.ValidationError('UPC is already exists.')
            return self.cleaned_data['upc']
        raise forms.ValidationError('Please add UPC.')


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

        product_set = Product.objects.filter(is_approved='Approved', product_class__name__in=['Rent'],is_deleted=False)

        if self_product_q:
            product_set = product_set.exclude(id__in=self_product_q.values_list('id', flat=True))

        # for vendor
        if product_user.is_staff and not product_user.is_superuser:

            vendor_user = Partner.objects.get(users=product_user)
            vendor_stock = StockRecord.objects.filter(partner=vendor_user).values_list('product', flat=True)
            product_set = product_set.filter(id__in=vendor_stock)

        self.fields['combo_product'].queryset = product_set
        self.fields['product'].queryset = Product.objects.filter(id=self_product,is_deleted=False)
        self.initial['product'] = Product.objects.get(id=self_product)