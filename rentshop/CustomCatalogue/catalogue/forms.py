# python imports
import datetime

# django imports
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxLengthValidator

# 3rd party imports
from oscar.apps.catalogue.reviews.forms import ProductReviewForm
from captcha.fields import CaptchaField
from oscar.core.loading import get_model

# internal imports
Vote = get_model('reviews', 'vote')
Category = get_model('catalogue', 'Category')
CategoriesWiseFilterValue = get_model('catalogue', 'CategoriesWiseFilterValue')
PremiumProducts = get_model('catalogue', 'PremiumProducts')
Product = get_model('catalogue', 'Product')
Enquiry = get_model('customer', 'Enquiry')

ProductReview = get_model('reviews', 'productreview')
PRICE_RANGE = (
    ('', 'Select Price'),
    ('1-100', '1-100'),
    ('100-300', '100-300'),
    ('300-500', '300-500'),
    ('500-1000', '500-1000'),
    ('1000-2000', '1000-2000'),
    ('2000-3000', '2000-3000'),
    ('3000-4000', '3000-4000'),
    ('4000-5000', '4000-5000'),
    ('5000-6000', '5000-6000'),
    ('6000-7000', '6000-7000'),
    ('7000-8000', '7000-8000'),
    ('8000-9000', '8000-9000'),
    ('9000-10000', '9000-10000'),
    ('10000-20000', '10000-20000'),
    ('20000-30000', '20000-30000'),
    ('30000-40000', '30000-40000'),
    ('40000-50000', '40000-50000'),
    ('50000-60000', '50000-60000'),
    ('60000-70000', '60000-70000'),
    ('70000-80000', '70000-80000'),
    ('80000-90000', '80000-90000'),
    ('90000-100000', '90000-100000'),
    ('100000-110000', '100000-110000'),
    ('110000-150000', '110000-150000'),
)
EVENTS = (
    ('', 'Select Event'),
    ('0', 'Diwali'),
)


class CustomProductReviewForm(ProductReviewForm):

    """
    Product review model form
    """

    title = forms.CharField(min_length=2, label=_('Title'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    body = forms.CharField(max_length=255, widget=forms.Textarea)
    name = forms.CharField(label=_('Name'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)

    # captcha = CaptchaField()

    class Meta:
        model = ProductReview
        fields = ('name', 'email','title', 'score', 'body',)

    def __init__(self, product, user=None, *args, **kwargs):
        super(ProductReviewForm, self).__init__(*args, **kwargs)
        self.instance.product = product
        if user and user.is_authenticated:
            self.instance.user = user

class CustomProductReviewForm1(ProductReviewForm):

    """
    Product review model form
    """

    title = forms.CharField(min_length=2, label=_('Title'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    body = forms.CharField(max_length=255, widget=forms.Textarea)
    name = forms.CharField(label=_('Name'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)

    class Meta:
        model = ProductReview
        fields = ('title', 'score', 'body', 'name', 'email')



class BrowseSearchForm(forms.Form):

    """
    Catalogue search form.
    """

    mega_search = forms.CharField(max_length=100, required=False)
    price_range = forms.ChoiceField(choices=PRICE_RANGE, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(show_on_frontside = True), required=False)
    event = forms.ChoiceField(choices=EVENTS, required=False)
    venues = forms.ModelChoiceField(
        queryset=Category.objects.filter(name__in=('Lawn/Halls', '5 Star Hotels', 'Resorts', 'Hotels / 5 Star hotels', 'Lawns / Banquet Halls')),
        required=False
    )
    filter_list = forms.CharField(max_length=100,required=False)

    def __init__(self, *args, **kwargs):
        category = kwargs.pop("category")
        super(BrowseSearchForm, self).__init__(*args, **kwargs)
        self.fields['mega_search'].widget.attrs['class'] = 'form-control'
        self.fields['price_range'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['event'].widget.attrs['class'] = 'form-control'
        self.fields['venues'].widget.attrs['class'] = 'form-control'
        self.fields['filter_list'].widget = forms.HiddenInput()

        if category:
            id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
            self.fields['category'].queryset = Category.objects.filter(id__in=id_list)
            # CategoriesWiseFilterValue.objects.filter(category__name = category)
        else:
            cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)
            cat_list = []
            for category in cat_obj:
                id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
                for element in id_list:
                    cat_list.append(element)
            self.fields['category'].queryset = Category.objects.filter(id__in=cat_list)


class AdminPremiumProductsForm(forms.ModelForm):

    """
    Product premium  model form
    """
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={'onchange': 'get_products();'}))

    class Meta:
        model = PremiumProducts
        fields = '__all__'

    def clean_product(self):
        product = self.cleaned_data['product']
        if len(product) > 9:
            raise forms.ValidationError('You can add maximum 9 product')
        return product


class EnquiryModelForm(forms.ModelForm):

    """
    Model form to validate/save best qoute.
    """

    RENTAL_DURATION_CHOICES = (
        (1, 'One'),
        (2, 'Two'),
        (3, 'Three'),
        (4, 'Four'),
    )

    EVENT_CHOICE = [
        ('1', 'Annual'),
        ('2', 'Festival'),
        ('3', 'Concert'),
        ('4', 'Exhibition'),
        ('5', 'Fashion Show'),
        ('6', 'Customized Wedding'),
        ('7', 'Customized Birthday'),
        ('8', 'Other'),
    ]

    email = forms.EmailField()

    organization_name = forms.CharField(required=True, validators=[RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid organisation name.')])
    person_name = forms.CharField(required=True, validators=[RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid name.')])
    enquiry_date = forms.DateTimeField(widget=forms.DateTimeInput(),required=True)
    rental_duration = forms.CharField(widget=forms.RadioSelect(choices=RENTAL_DURATION_CHOICES))
    telephone_number = forms.CharField(required=True, min_length=10, max_length=10, validators=[RegexValidator('^[6789]\d{9}$', message='Enter a valid mobile number.')])
    budget_from = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Minimum', 'class':'form-control-qoute'
            }
        ),
        validators=[RegexValidator('^([0-9])+$', message='Enter a valid Amount.')],

    )
    budget_to = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Maximum', 'class': 'form-control-qoute'
            }
        ),
        validators=[RegexValidator('^([0-9])+$', message='Enter a valid Amount.')],

    )
    class Meta:
        model = Enquiry
        fields = (
            'organization_name', 'person_name', 'telephone_number',
            'email','enquiry_date', 'event_type','created_by',
            'rental_duration', 'budget_from',  'budget_to',
        )

        exclude = ('updated_by','date_created','date_updated','allocated_vendor','enquiry_text','city','event_date',)

    def __init__(self, *args, **kwargs):

        super(EnquiryModelForm, self).__init__(*args, **kwargs)

        self.fields['organization_name'].widget.attrs['class'] = 'form-control-qoute'
        self.fields['organization_name'].widget.attrs['placeholder'] = 'Organisation Name'

        self.fields['email'].widget.attrs['class'] = 'form-control-qoute'

        self.fields['person_name'].widget.attrs['class'] = 'form-control-qoute'
        self.fields['person_name'].widget.attrs['placeholder'] = 'Contact Person Name'

        self.fields['telephone_number'].widget.attrs['class'] = 'form-control-qoute'
        self.fields['telephone_number'].widget.attrs['placeholder'] = 'Contact Mobile Number'

        self.fields['enquiry_date'].widget.attrs['class'] = 'form-control-qoute'
        self.fields['enquiry_date'].widget.attrs['placeholder'] = 'Event Date'

        self.fields['budget_from'].required = True
        self.fields['budget_to'].required = True


        self.fields['created_by'].widget = forms.HiddenInput()

    def clean_budget_to(self):

        budget_to = self.cleaned_data.get('budget_to',False)
        budget_from = self.cleaned_data.get('budget_from',False)

        if budget_from and budget_to:
            bud_from = int(budget_from)
            bud_to = int(budget_to)

            if bud_to < 1:
                raise forms.ValidationError('Please select valid budget.')

            if bud_from and bud_to and bud_from > bud_to:
                raise forms.ValidationError('Please give budget to figure greater than budget from')
            return budget_to
        else:
            raise forms.ValidationError('Please enter budget.')

        return budget_to

    def clean_budget_from(self):

        budget_from = self.cleaned_data.get('budget_from')
        bud_from = int(budget_from)

        if bud_from:
            if bud_from < 1:
                raise forms.ValidationError('Please select valid budget.')
            return budget_from

    def clean(self):

        budget_from = self.cleaned_data.get('budget_from')
        budget_to = self.cleaned_data.get('budget_to')
        if budget_to and budget_from:
            bud_from = int(budget_from)
            bud_to = int(budget_to)

            if bud_from and bud_to and bud_from > bud_to:
                raise forms.ValidationError('Please give budget to figure greater than budget from')


    def clean_enquiry_date(self):

        enquiry_date = self.cleaned_data['enquiry_date']

        if enquiry_date < datetime.datetime.now():
            raise forms.ValidationError('Please select future date')
        return enquiry_date
