# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django_select2.forms import Select2Widget, Select2MultipleWidget

# package import
from oscar.core.loading import get_class, get_model

# internal imports
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')

PremiumProducts = get_model('catalogue', 'PremiumProducts')

PRODUCT_STATUS = (
    ('', 'Select type'),
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Disapproved', 'Disapproved')
)


class PremiumSearchForm(forms.Form):

    category_title = forms.CharField(required=False, max_length=100)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)

class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.upc

class PremiumProductsModelForm(forms.ModelForm):


    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={'onchange': 'get_products();'}))
    product = MyModelMultipleChoiceField(queryset=Product.objects.filter(is_approved='Approved', is_deleted=False))
    # product = forms.ModelChoiceField(queryset=Product.objects.filter(is_approved='Approved'))
    class Meta:
        model = PremiumProducts
        fields = ('category', 'product')

    def __init__(self, *args, **kwargs):
        prod_obj = Product.objects.filter(is_approved='Approved', is_deleted=False)

        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = prod_obj

    def clean_product(self):
        product = self.cleaned_data['product']
        if len(product) > 12:
            raise forms.ValidationError('You can add maximum 12 product')
        return product


class PremiumProductAddForm(forms.ModelForm):

    """
    Form to store premium product.
    """
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    product = MyModelMultipleChoiceField(queryset=Product.objects.filter(is_approved='Approved', is_deleted=False), widget= Select2MultipleWidget)

    class Meta:
        model = PremiumProducts
        fields = ('category', 'product')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            cat = Category.objects.get(id=self.instance.category.id)
            prods = cat.product_set.filter(is_approved='Approved',is_deleted = False)
            self.fields['category'].initial = self.instance.category.id
            self.fields['category'].disabled  = True
            self.fields['product'].queryset = prods
            self.fields['category'].required = False
            self.fields['product'].widget.attrs['class'] = 'premium_product'

    def clean_product(self):
        product = self.cleaned_data['product']
        if len(product) > 12:
            raise forms.ValidationError('You can add maximum 12 product')
        return product

    def clean_category(self):
        category = self.cleaned_data['category']
        if self.instance.pk :
            return self.instance.category
        return self.cleaned_data['category']