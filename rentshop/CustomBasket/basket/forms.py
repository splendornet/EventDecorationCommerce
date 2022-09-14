# python imports
import datetime

# django imports
from django import forms
from django.conf import settings
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

# 3rd party imports
from oscar.core.loading import get_model, get_class
from oscar.forms import widgets

# internal imports
from .bind import *

Line = get_model('basket', 'line')
Basket = get_model('basket', 'basket')
Product = get_model('catalogue', 'product')
StockRecord = get_model('partner', 'stockrecord')
get_product_blocked_date = get_class('catalogue.bind', 'get_product_blocked_date')


class BasketLineForm(forms.ModelForm):

    """
    Form to save cart lines
    """

    save_for_later = forms.BooleanField(initial=False, required=False, label=_('Save for Later'))
    booking_start_date = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'class':'date_1'}))
    booking_end_date = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'class':'date_2'}))
    quantity = forms.IntegerField()
    prod_id = forms.CharField(max_length=10, required=False)
    line_id = forms.CharField(max_length=10, required=False)

    def __init__(self, strategy, *args, **kwargs):

        """
        Model form default init method.
        :param strategy: cart discount type
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)

        self.instance.strategy = strategy
        max_allowed_quantity = None

        self.fields['booking_start_date'].widget = forms.HiddenInput()
        self.fields['booking_end_date'].widget = forms.HiddenInput()
        self.fields['quantity'].widget.attrs['class'] = 'quantity_update'
        self.fields['prod_id'].widget = forms.HiddenInput()
        self.fields['line_id'].widget = forms.HiddenInput()

        num_available = getattr(self.instance.purchase_info.availability, 'num_available', None)
        basket_max_allowed_quantity = self.instance.basket.max_allowed_quantity()[0]

        if all([num_available, basket_max_allowed_quantity]):
            max_allowed_quantity = min(num_available, basket_max_allowed_quantity)
        else:
            max_allowed_quantity = num_available or basket_max_allowed_quantity

        if max_allowed_quantity:
            self.fields['quantity'].widget.attrs['max'] = max_allowed_quantity

    def clean_quantity(self):

        """
        Form clean method to check product quantity validation.
        :return: validation
        """

        qty = self.cleaned_data['quantity']

        if qty > 0:
            self.check_max_allowed_quantity(qty)
            self.check_permission(qty)

        return qty

    def check_max_allowed_quantity(self, qty):

        """
        Method to check cart product quantity is allowed.
        :param qty: cart product quantity
        :return: validation
        """

        qty_delta = qty - self.instance.quantity
        is_allowed, reason = self.instance.basket.is_quantity_allowed(qty_delta)
        if not is_allowed:
            raise forms.ValidationError(reason)

    def check_permission(self, qty):

        """
        Method to check permission for product buying
        :param qty: cart product quantity
        :return: validation
        """

        policy = self.instance.purchase_info.availability
        is_available, reason = policy.is_purchase_permitted(
            quantity=qty)
        if not is_available:
            raise forms.ValidationError(reason)

    class Meta:
        model = Line
        fields = ['quantity', 'booking_start_date','booking_end_date',]


class SavedLineForm(forms.ModelForm):

    """
    Save cart lines model form.
    """

    move_to_basket = forms.BooleanField(initial=False, required=False, label=_('Move to Basket'))

    class Meta:
        model = Line
        fields = ('id', 'move_to_basket')

    def __init__(self, strategy, basket, *args, **kwargs):

        """
        Model for default init method
        :param strategy: cart discount type
        :param basket: cart instance
        :param args: default
        :param kwargs: default
        """

        self.strategy = strategy
        self.basket = basket
        super().__init__(*args, **kwargs)

    def clean(self):

        """
        Form clean method to validate form fields
        :return: validation
        """

        cleaned_data = super().clean()

        if not cleaned_data['move_to_basket']:
            return cleaned_data

        lines = self.basket.lines.filter(product=self.instance.product)
        current_qty = lines.aggregate(Sum('quantity'))['quantity__sum'] or 0
        desired_qty = current_qty + self.instance.quantity

        result = self.strategy.fetch_for_product(self.instance.product)
        is_available, reason = result.availability.is_purchase_permitted(quantity=desired_qty)
        if not is_available:
            raise forms.ValidationError(reason)
        return cleaned_data


class BasketVoucherForm(forms.Form):

    """
    Form for basket vouchers.
    """

    code = forms.CharField(max_length=128, label=_('Code'))

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)

    def clean_code(self):

        """
        Form clean method to validate coupon code.
        :return: validation
        """

        return self.cleaned_data['code'].strip().upper()


class AddToBasketForm(forms.Form):

    """
    Form to add product to basket.
    """

    quantity = forms.IntegerField(label=_('Quantity'))
    order_type = forms.CharField(required=False)
    add_to_cart = forms.CharField(required=False)
    booking_start_date = forms.CharField(required=False)
    booking_end_date = forms.CharField(required=False)
    product_attributes = forms.CharField(required=False)
    flower_type = forms.CharField(required=False)

    def __init__(self, basket, product, *args, **kwargs):

        """
        Form default init method.
        :param basket: basket instance
        :param product: product instance
        :param args: default
        :param kwargs: default
        """

        self.basket = basket
        self.parent_product = product

        super().__init__(*args, **kwargs)

        self.fields['booking_start_date'].widget = forms.HiddenInput()
        self.fields['booking_end_date'].widget = forms.HiddenInput()
        self.fields['product_attributes'].widget = forms.HiddenInput()
        self.fields['flower_type'].widget = forms.HiddenInput()

        # Dynamically build fields
        if product.is_parent:
            self._create_parent_product_fields(product)

        self._create_product_fields(product)

    def _create_parent_product_fields(self, product):

        """
        Method to create product parent field.
        :param product: product
        :return:
        """

        choices = []
        disabled_values = []
        for child in product.children.all():
            attr_summary = child.attribute_summary
            if attr_summary:
                summary = attr_summary
            else:
                summary = child.get_title()

            # Check if it is available to buy
            info = self.basket.strategy.fetch_for_product(child)
            if not info.availability.is_available_to_buy:
                disabled_values.append(child.id)

            choices.append((child.id, summary))

        self.fields['child_id'] = forms.ChoiceField(
            choices=tuple(choices), label=_("Variant"),
            widget=widgets.AdvancedSelect(disabled_values=disabled_values)
        )

    def _create_product_fields(self, product):

        """
        Method to add the product option fields.
        :param product: product instance
        :return: None
        """

        for option in product.options:
            self._add_option_field(product, option)

    def _add_option_field(self, product, option):

        """
        Method to create the appropriate form field for the product option.
        :param product: product instance
        :param option: options
        :return: None
        """

        self.fields[option.code] = forms.CharField(label=option.name, required=option.is_required)

    def clean_child_id(self):

        """
        Form clean method to validate child id.
        :return: validation
        """

        try:
            child = self.parent_product.children.get(id=self.cleaned_data['child_id'])
        except Product.DoesNotExist:
            raise forms.ValidationError(_("Please select a valid product"))

        self.child_product = child
        return self.cleaned_data['child_id']

    def clean_quantity(self):

        """
        Form clean method to validate quantity.
        :return: validation
        """

        qty = self.cleaned_data['quantity']

        if qty == 0:
            raise forms.ValidationError('Please select valid quantity.')

        min_qty = qty

        basket_threshold = settings.OSCAR_MAX_BASKET_QUANTITY_THRESHOLD
        if basket_threshold:
            total_basket_quantity = self.basket.num_items
            max_allowed = basket_threshold - total_basket_quantity
            if qty > max_allowed:
                raise forms.ValidationError(
                    _("Due to technical limitations we are not able to ship"
                      " more than %(threshold)d items in one order. Your"
                      " basket currently has %(basket)d items.")
                    % {'threshold': basket_threshold,
                       'basket': total_basket_quantity}
                )
        return min_qty

    @property
    def product(self):

        """
        Form property to return product.
        :return: product
        """

        return getattr(self, 'child_product', self.parent_product)

    def clean(self):

        """
        Form clean method.
        :return: validation.
        """

        # validate blocked dates.

        # calculate product qty.

        # raise forms.ValidationError('!!!!')

        qty = self.cleaned_data.get('quantity')
        start_date = self.cleaned_data.get('booking_start_date')
        end_date = self.cleaned_data.get('booking_end_date')


        if self.product.product_class.name in 'Professional':
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %I:%M %p')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %I:%M %p')

        else:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        total_days = end_date - start_date
        booking_days = total_days.days + 1

        qty_validator = bind_product_quantity(self.product, qty, self.cleaned_data.get('order_type'), booking_days)

        if qty_validator == '1':
            raise forms.ValidationError('Please select valid quantity')

        if qty_validator == '2':
            raise forms.ValidationError('Something went wrong.')

        if self.cleaned_data.get('booking_start_date'):

            if self.product.product_class.name in 'Rent':
                cleaned_date = self.cleaned_data.get('booking_start_date')
                cleaned_date = datetime.datetime.strptime(str(cleaned_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            if self.product.product_class.name in 'Professional':
                cleaned_date = self.cleaned_data.get('booking_start_date')
                cleaned_date = datetime.datetime.strptime(str(cleaned_date), '%Y-%m-%d %I:%M %p').strftime('%m/%d/%Y')

            cleaned_date = self.cleaned_data.get('booking_start_date')
            if str(cleaned_date) in get_product_blocked_date(self.product.id):
                raise forms.ValidationError("Product not available.")

        info = self.basket.strategy.fetch_for_product(self.product)

        # Check that a price was found by the strategy
        if not info.price.exists:
            raise forms.ValidationError(
                _("This product cannot be added to the basket because a "
                  "price could not be determined for it.")
            )

        # Check currencies are sensible
        if (self.basket.currency and info.price.currency != self.basket.currency):
            raise forms.ValidationError(
                _("This product cannot be added to the basket as its currency "
                  "isn't the same as other products in your basket")
            )

        # Check user has permission to add the desired quantity to their
        # basket.

        current_qty = self.basket.product_quantity(self.product)
        desired_qty = current_qty + self.cleaned_data.get('quantity', 1)
        is_permitted, reason = info.availability.is_purchase_permitted(desired_qty)
        if not is_permitted:
            raise forms.ValidationError(reason)

        return self.cleaned_data

    def cleaned_options(self):

        """
        Method to return submitted options in a clean format
        :return: validation
        """

        options = []

        for option in self.parent_product.options:

            if option.code in self.cleaned_data:
                options.append(
                    {
                        'option': option,
                        'value': self.cleaned_data[option.code]
                    }
                )

        return options


class SimpleAddToBasketForm(AddToBasketForm):

    """
    Oscar extended basket form.
    """

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super().__init__(*args, **kwargs)
        if 'quantity' in self.fields:
            self.fields['quantity'].initial = 1
            self.fields['quantity'].widget = forms.HiddenInput()
            self.fields['order_type'].widget = forms.HiddenInput()
            self.fields['add_to_cart'].widget = forms.HiddenInput()

