# python imports
import datetime
from datetime import timedelta
from decimal import Decimal as D, InvalidOperation
from decimal import ROUND_UP
import logging, json, csv, re, itertools, random

# django imports
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.db.models import Avg, Count, Sum
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import HttpResponse

# 3rd party imports
from oscar.apps.dashboard.reviews import views as review_view
from oscar.apps.dashboard.catalogue.views import ProductCreateUpdateView, filter_products, CategoryListView
from oscar.apps.dashboard.catalogue.views import ProductListView
from oscar.apps.dashboard.partners.views import PartnerListView, PartnerCreateView, PartnerManageView, PartnerDeleteView, PartnerUserCreateView, PartnerUserSelectView
from oscar.apps.dashboard.views import IndexView
from oscar.core.loading import get_classes, get_model
from oscar.core.compat import get_user_model
from oscar.apps.dashboard.orders.views import OrderListView, get_order_for_user_or_404
from oscar.core.utils import datetime_combine, format_datetime
from oscar.apps.dashboard.vouchers.views import VoucherCreateView, VoucherUpdateView, VoucherListView, VoucherDeleteView,VoucherStatsView
from oscar.apps.dashboard.partners.views import PartnerDeleteView

from oscar.views import sort_queryset
from oscar.apps.checkout.signals import post_checkout
from oscar.core.loading import get_class, get_model
from oscar.apps.dashboard.users.views import IndexView as UserIndexView
from oscar.apps.customer.utils import normalise_email
from . import decorators as decor

# internal imports
from .tables import CustomCategoryTable
from CustomDashboard.dashboard.formsets import CustomStockRecordFormSet
from oscar.apps.dashboard.ranges.views import RangeCreateView
from . import utils
from .forms import CustomProductReviewSearchForm
from . import forms as dash_form


# class
UserForm = get_class('partner.forms', 'User_Form')
VendorCalendarAddEvent = get_class('dashboard.forms', 'VendorCalendarAddEvent')
OrderCreator = get_class('order.utils', 'OrderCreator')
Dispatcher = get_class('customer.utils', 'Dispatcher')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')
logger = logging.getLogger('oscar.checkout')
RelatedFieldWidgetWrapper = get_class('dashboard.widgets', 'RelatedFieldWidgetWrapper')



CustomRangeForm = get_class('dashboard.forms', 'CustomRangeForm')
CustomRangeForm1 = get_class('dashboard.forms', 'CustomRangeForm1')

CustomUserSearchForm = get_class('dashboard.forms', 'CustomUserSearchForm')
(PartnerSearchForm, PartnerCreateForm, PartnerAddressForm,
 NewUserForm, UserEmailForm, ExistingUserForm) = get_classes(
    'dashboard.partners.forms',
    ['PartnerSearchForm', 'PartnerCreateForm', 'PartnerAddressForm',
     'NewUserForm', 'UserEmailForm', 'ExistingUserForm']
)
CustomPartnerForm = get_class('partner.forms', 'PartnerForm')
PartnerUpdateForm = get_class('partner.forms', 'PartnerUpdateForm')
VendorStatusSearchForm_c = get_class('dashboard.forms', 'CustomPartnerSearchForm')
(ProductForm,
 ProductClassSelectForm,
 ProductSearchForm,
 ProductClassForm,
 CategoryForm,
 StockAlertSearchForm,
 AttributeOptionGroupForm) \
    = get_classes('dashboard.catalogue.forms',
                  ('ProductForm',
                   'ProductClassSelectForm',
                   'ProductSearchForm',
                   'ProductClassForm',
                   'CategoryForm',
                   'StockAlertSearchForm',
                   'AttributeOptionGroupForm'))
(StockRecordFormSet,
 ProductCategoryFormSet,
 ProductImageFormSet,
 ProductRecommendationFormSet,
 ProductAttributesFormSet,
 AttributeOptionFormSet) \
    = get_classes('dashboard.catalogue.formsets',
                  ('StockRecordFormSet',
                   'ProductCategoryFormSet',
                   'ProductImageFormSet',
                   'ProductRecommendationFormSet',
                   'ProductAttributesFormSet',
                   'AttributeOptionFormSet'))

ProductTable, CategoryTable, AttributeOptionGroupTable \
    = get_classes('dashboard.tables',
                  ('CustomProductTable', 'CategoryTable',
                   'AttributeOptionGroupTable'))
UserTable = get_class('dashboard.tables', 'CustomUserTable')
EventHandler = get_class('order.processing', 'EventHandler')
OrderStatsForm = get_class('dashboard.orders.forms', 'OrderStatsForm')
OrderSearchForm = get_class('dashboard.orders.forms', 'OrderSearchForm')
OrderNoteForm = get_class('dashboard.orders.forms', 'OrderNoteForm')
ShippingAddressForm = get_class('dashboard.orders.forms', 'ShippingAddressForm')
OrderStatusForm = get_class('dashboard.orders.forms', 'OrderStatusForm')
CustProductCategoryFormSet = get_class('dashboard.formsets', 'ProductCategoryFormSet')
CustProductImageFormSet = get_class('dashboard.formsets', 'CustomProductImageFormSet')
AttributeFormSet = get_class('dashboard.formsets', 'AttributeFormSet')

ComboProductFormSet = get_class('dashboard.formsets', 'ComboProductFormSet')

ComboStockRecordFormSet = get_class('dashboard.formsets', 'ComboStockRecordFormSet')
ComboProductCategoryFormSet = get_class('dashboard.formsets', 'ComboProductCategoryFormSet')
ComboProductForm = get_class('dashboard.forms', 'ComboProductForm')

(PopUpWindowCreateMixin,
 PopUpWindowUpdateMixin,
 PopUpWindowDeleteMixin) \
    = get_classes(
    'dashboard.views',
    (
        'PopUpWindowCreateMixin',
        'PopUpWindowUpdateMixin',
        'PopUpWindowDeleteMixin'
    )
)
ProductTypeUpdateForm = get_class('dashboard.forms', 'ProductTypeUpdateForm')
ProductFormClass = get_class('dashboard.forms', 'CustomProductForm')
CustomProductSearchForm = get_class('dashboard.forms', 'CustomProductSearchForm')
ProductUnitModelForm = get_class('dashboard.forms', 'ProductUnitModelForm')
ProductUnitUpdateModelForm = get_class('dashboard.forms', 'ProductUnitUpdateModelForm')
ProductUnitSearchForm = get_class('dashboard.forms', 'ProductUnitSearchForm')
VoucherForm = get_class('dashboard.forms', 'CustomVoucherForm')
VoucherForm1 = get_class('dashboard.forms', 'CustomVoucherForm1')

VoucherSearchForm = get_class('dashboard.forms', 'CustomVoucherSearchForm')
ComboSearchForm = get_class('dashboard.forms', 'ComboSearchForm')
CustomDashboardProductReviewForm = get_class('dashboard.forms', 'CustomDashboardProductReviewForm')
ComboProductSetForm = get_class('dashboard.forms', 'ComboProductSetForm')

# models
UserAddress = get_model('address', 'UserAddress')

User = get_user_model()
CustomProfile = get_model('customer', 'CustomProfile')
CommunicationEventType = get_model('customer', 'CommunicationEventType')

Notes = get_model('customer', 'Notes')
VendorCalender = get_model('partner', 'VendorCalender')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')

Basket = get_model('basket', 'Basket')
Basket_Line = get_model('basket', 'Line')

ConditionalOffer = get_model('offer', 'ConditionalOffer')
CustomizeCouponModel = get_model('offer', 'CustomizeCouponModel')
Voucher = get_model('voucher', 'Voucher')

Partner = get_model('partner', 'Partner')
StockAlert = get_model('partner', 'StockAlert')
StockRecord = get_model('partner', 'StockRecord')
_VendorCalender = get_model('partner', 'VendorCalender')
ProductUnit = get_model('partner', 'ProductUnit')

Range = get_model('offer', 'Range')

Transaction = get_model('payment', 'Transaction')
SourceType = get_model('payment', 'SourceType')

Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
OrderNote = get_model('order', 'OrderNote')
ShippingAddress = get_model('order', 'ShippingAddress')
Line = get_model('order', 'Line')
ShippingEventType = get_model('order', 'ShippingEventType')
PaymentEventType = get_model('order', 'PaymentEventType')
BillingAddress = get_model('order', 'BillingAddress')
PaymentEvent = get_model('order', 'PaymentEvent')
PaymentEventQuantity = get_model('order', 'PaymentEventQuantity')
OrderAllocatedVendor = get_model('order', 'OrderAllocatedVendor')

Product = get_model('catalogue', 'Product')
ComboProducts = get_model('catalogue', 'ComboProducts')
Category = get_model('catalogue', 'Category')
ProductImage = get_model('catalogue', 'ProductImage')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductClass = get_model('catalogue', 'ProductClass')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')
ProductReview = get_model('reviews', 'productreview')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')
Attribute = get_model('catalogue', 'Attribute')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')
send_sms = get_class('RentCore.email', 'send_sms')


class ComboOfferIndexView(generic.ListView):
    """
    Combo offer index page view.
    """

    template_name = 'dashboard/combo/index.html'
    model = Product
    context_object_name = 'combo_offer'
    paginate_by = 20
    form_class = ComboSearchForm

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            data = self.request.GET
            product_class = ProductClass.objects.get(name='Combo')

            if self.request.user.is_superuser:
                queryset = Product.objects.filter(product_class=product_class, is_deleted=False)

            if self.request.user.is_staff and not self.request.user.is_superuser:
                user = User.objects.get(id=self.request.user.id)
                partner = Partner.objects.filter(users=user).last()
                partner_stocks = StockRecord.objects.filter(partner=partner).values_list('product__id', flat=True)
                queryset = Product.objects.filter(product_class=product_class, id__in=partner_stocks, is_deleted=False)

            if data.get('product_title'):
                product_title = data.get('product_title')
                queryset = queryset.filter(title__icontains=product_title)

            if data.get('upc'):
                upc = data.get('upc')
                queryset = queryset.filter(upc=upc)

            if data.get('status'):
                queryset = queryset.filter(is_approved=data.get('status'))

            if data.get('vendor_name'):
                partner = Partner.objects.filter(name__icontains=data.get('vendor_name'))
                stock_record = StockRecord.objects.filter(partner__id__in=partner.values_list('id', flat=True))
                queryset = queryset.filter(id__in=stock_record.values_list('product', flat=True))

            return queryset

        except Exception as e:
            print(e.args)
            return []

    def get_context_data(self, **kwargs):

        ctx = super(ComboOfferIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class ProductComboDeleteView(generic.View):
    template_name = 'dashboard/combo/combo_product_delete.html'

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        product = None

        if not pk:
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard/')

        try:
            product = Product.objects.get(id=pk)
        except:
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard/')

        context = {}
        context['product'] = product

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = request.POST.get('product_pk')

        if not pk:
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard/')

        try:
            product = Product.objects.get(id=pk)
            Product.objects.filter(id=pk).delete()
            messages.success(request, 'Combo product deleted successfully.')
            return redirect('/dashboard/catalogue/combo/index/')
        except:
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard/')


class ProductComboCreateRedirectView(generic.RedirectView):
    permanent = False
    productclass_form_class = ProductClassSelectForm

    def get_product_create_url(self, product_class):
        return reverse(
            'dashboard:combo-create-update',
            kwargs={'product_class_slug': product_class.slug}
        )

    def get_invalid_product_class_url(self):
        messages.error(self.request, _("Please choose a product type"))
        return reverse('dashboard:catalogue-product-list')

    def get_redirect_url(self, **kwargs):

        try:
            product_combo = ProductClass.objects.get(name='Combo')
            return self.get_product_create_url(product_combo)
        except Exception as e:
            messages.error(self.request, 'Combo offer is not yet ready.')
            return reverse('dashboard:catalogue-product-list')


class CreateUpdateCombo(ProductCreateUpdateView):
    """
    Combo view that can both create and update view.
    """

    template_name = 'dashboard/combo/createupdate_combo.html'

    form_class = ComboProductForm

    category_formset = ComboProductCategoryFormSet
    stockrecord_formset = ComboStockRecordFormSet
    comboproduct_formset = ComboProductFormSet
    ComboProductSetForm = ComboProductSetForm

    def __init__(self, *args, **kwargs):

        super(CreateUpdateCombo, self).__init__(*args, **kwargs)

        self.formsets = {
            'category_formset': self.category_formset,
            'image_formset': self.image_formset,
            'recommended_formset': self.recommendations_formset,
            'stockrecord_formset': self.stockrecord_formset,
            'comboproduct_formset': self.comboproduct_formset,
        }

    def get_context_data(self, **kwargs):

        ctx = super(CreateUpdateCombo, self).get_context_data(**kwargs)

        ctx['product_class'] = self.product_class
        ctx['parent'] = self.parent
        ctx['title'] = self.get_page_title()

        for ctx_name, formset_class in self.formsets.items():
            if ctx_name not in ctx:
                ctx[ctx_name] = formset_class(self.product_class, self.request.user, instance=self.object)
        return ctx

    def get_page_title(self):

        if self.creating:
            if self.parent is None:
                return _('Create new %(product_class)s product') % {'product_class': self.product_class.name}
            else:
                return _('Create new variant of %(parent_product)s') % {'parent_product': self.parent.title}
        else:
            if self.object.title or not self.parent:
                return self.object.title
            else:
                return _('Editing variant of %(parent_product)s') % {'parent_product': self.parent.title}

    def get_success_url(self):

        messages.success(self.request, 'Record saved successfully.', extra_tags="safe noicon")

        action = self.request.POST.get('action')
        if action == 'continue':
            url = reverse('dashboard:combo-create-update', kwargs={"pk": self.object.id})
        else:
            url = reverse('dashboard:combo-index')

        return self.get_url_with_querystring(url)

    def forms_valid(self, form, formsets):

        """
        Save all changes and display a success url.
        When creating the first child product, this method also sets the new
        parent's structure accordingly.
        """

        if self.creating:
            self.handle_adding_child(self.parent)
        else:
            self.object = form.save()

        for formset in formsets.values():
            formset.save()

        for idx, image in enumerate(self.object.images.all()):
            image.display_order = idx
            image.save()

        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, formsets):

        if self.creating and self.object and self.object.pk is not None:
            self.object.delete()
            self.object = None

        messages.error(self.request, _("Your submitted data was not valid - please correct the errors below"))
        ctx = self.get_context_data(form=form, **formsets)

        return self.render_to_response(ctx)

    def process_all_forms(self, form):

        """
        Short-circuits the regular logic to have one place to have our
        logic to check all forms
        """

        if self.creating and form.is_valid():
            self.object = form.save()

        formsets = {}

        for ctx_name, formset_class in self.formsets.items():
            formsets[ctx_name] = formset_class(self.product_class, self.request.user, self.request.POST,
                                               self.request.FILES, instance=self.object)

        is_valid = form.is_valid() and all([formset.is_valid() for formset in formsets.values()])

        cross_form_validation_result = self.clean(form, formsets)

        if is_valid and cross_form_validation_result:
            return self.forms_valid(form, formsets)
        else:
            return self.forms_invalid(form, formsets)

    form_valid = form_invalid = process_all_forms


class IndexViewCustom(IndexView):
    """
    Dashboard index page view.
    """

    def get_template_names(self):
        if self.request.user.is_staff:
            return ['dashboard/index.html', ]
        else:
            return ['dashboard/index_nonstaff.html', 'dashboard/index.html']

    def get_vendor(self):
        is_vendor = self.request.user.groups.filter(name='Vendor').exists()
        vendor_obj = {
            'isVendor': is_vendor,
        }
        return vendor_obj

    def get_vendor_obj(self):
        user_type = None
        is_vendor = self.request.user.groups.filter(name='Vendor').exists()
        if is_vendor:
            user_type = 'Vendor'
            return user_type
        else:
            user_type = 'Admin'
            return user_type

    def get_open_baskets(self, filters=None):

        user_type_obj = self.get_vendor_obj()
        user_id = self.request.user.id
        if user_type_obj == 'Vendor':
            filters = {'owner_id': user_id}
        else:
            filters = {}
        filters['status'] = Basket.OPEN
        return Basket.objects.filter(**filters)

    def get_hourly_report(self, hours=24, segments=10):

        time_now = now().replace(minute=0, second=0)
        start_time = time_now - timedelta(hours=hours - 1)

        user_type_obj = self.get_vendor_obj()
        vendor_order_total = 0

        if user_type_obj == 'Vendor':
            partner_id = Partner.objects.get(users=self.request.user)
            stock_record = StockRecord.objects.filter(partner_id=partner_id.id).values_list('id')

            basket_line = Basket_Line.objects.filter(stockrecord_id__in=stock_record).values_list('basket_id')

            basket_obj = Basket.objects.filter(id__in=basket_line).values_list('id')
            orders_last_day_vendor = Order.objects.filter(basket_id__in=basket_obj, date_placed__gt=start_time)
            orders_last_day_vendors = OrderLine.objects.filter(partner_id=partner_id,
                                                               order_id__in=orders_last_day_vendor)

            vendor_order_total = orders_last_day_vendors.aggregate(
                Sum('line_price_incl_tax')
            )['line_price_incl_tax__sum'] or D('0.0')

            orders_last_day = Order.objects.filter(basket_id__in=basket_obj, date_placed__gt=start_time)
        else:
            orders_last_day = Order.objects.filter(date_placed__gt=start_time)
        user_type_obj = self.get_vendor_obj()
        order_total_hourly = []
        for hour in range(0, hours, 2):
            end_time = start_time + timedelta(hours=2)
            hourly_orders = orders_last_day.filter(date_placed__gt=start_time,
                                                   date_placed__lt=end_time)

            total = hourly_orders.aggregate(
                Sum('total_incl_tax')
            )['total_incl_tax__sum'] or D('0.0')
            order_total_hourly.append({
                'end_time': end_time,
                'total_incl_tax': total
            })
            start_time = end_time

        max_value = max([x['total_incl_tax'] for x in order_total_hourly])
        divisor = 1
        while divisor < max_value / 50:
            divisor *= 10
        max_value = (max_value / divisor).quantize(D('1'), rounding=ROUND_UP)
        max_value *= divisor
        if max_value:
            segment_size = (max_value) / D('100.0')
            for item in order_total_hourly:
                item['percentage'] = int(item['total_incl_tax'] / segment_size)

            y_range = []
            y_axis_steps = max_value / D(str(segments))
            for idx in reversed(range(segments + 1)):
                y_range.append(idx * y_axis_steps)
        else:
            y_range = []
            for item in order_total_hourly:
                item['percentage'] = 0

        ctx = {
            'order_total_hourly': order_total_hourly,
            'max_revenue': max_value,
            'y_range': y_range,
        }

        return ctx

    def get_stats(self):

        user_type_obj = self.get_vendor_obj()
        if user_type_obj == 'Vendor':
            partner_obj = Partner.objects.get(users=self.request.user)
            product_count_type = StockRecord.objects.filter(partner=partner_obj).count()
        else:
            product_count_type = Product.objects.count()

        datetime_24hrs_ago = now() - timedelta(hours=24)
        orders_line_total = OrderLine.objects.all()
        orders_last_day_vendor = OrderLine.objects.all()
        order_vendor_count = 0
        if user_type_obj == 'Vendor':
            partner_id = Partner.objects.get(users=self.request.user)
            stock_record = StockRecord.objects.filter(partner_id=partner_id.id).values_list('product_id')
            basket_line = Basket_Line.objects.filter(product_id__in=stock_record).values_list('basket_id')
            bakset_obj = Basket.objects.filter(id__in=basket_line).values_list('id')

            queryset = Order._default_manager.select_related(
                'billing_address', 'billing_address__country',
                'shipping_address', 'shipping_address__country',
                'user'
            ).prefetch_related('lines')

            partners = Partner.objects.filter(users=self.request.user)
            queryset = queryset.filter(lines__partner__in=partners).distinct()

            orders = Order.objects.filter(basket_id__in=bakset_obj)
            orders_last_24_hr = Order.objects.filter(basket_id__in=bakset_obj, date_placed__gt=datetime_24hrs_ago)
            orders_line_total = OrderLine.objects.filter(partner_id=partner_id, order_id__in=orders_last_24_hr)
            orders_line_total_id = OrderLine.objects.filter(partner_id=partner_id).values_list('order_id', flat=True)

            order_vendor_count = Order.objects.filter(id__in=orders_line_total_id).count()

            orders_last_day = orders.filter(basket_id__in=bakset_obj, date_placed__gt=datetime_24hrs_ago)
            orders_last_day_vendor = OrderLine.objects.filter(partner_id=partner_id, order_id__in=orders)
        else:
            orders = Order.objects.all()
            orders_last_day = orders.filter(date_placed__gt=datetime_24hrs_ago)

        open_alerts = StockAlert.objects.filter(status=StockAlert.OPEN)
        closed_alerts = StockAlert.objects.filter(status=StockAlert.CLOSED)

        total_lines_last_day = Line.objects.filter(
            order__in=orders_last_day).count()

        stats = {
            'total_orders_last_day': orders_last_day.count(),

            'total_lines_last_day': total_lines_last_day,

            'average_order_costs': orders_last_day.aggregate(
                Avg('total_incl_tax')
            )['total_incl_tax__avg'] or D('0.00'),

            'total_revenue_last_day': orders_last_day.aggregate(
                Sum('total_incl_tax')
            )['total_incl_tax__sum'] or D('0.00'),

            'hourly_report_dict': self.get_hourly_report(hours=24),

            'total_customers_last_day': User.objects.filter(
                date_joined__gt=datetime_24hrs_ago,
            ).count(),

            'total_open_baskets_last_day': self.get_open_baskets({
                'date_created__gt': datetime_24hrs_ago
            }).count(),

            'total_products': product_count_type,

            'total_open_stock_alerts': open_alerts.count(),

            'total_closed_stock_alerts': closed_alerts.count(),

            'total_site_offers': self.get_active_site_offers().count(),

            'total_vouchers': self.get_active_vouchers().count(),

            'total_promotions': self.get_number_of_promotions(),

            'total_customers': User.objects.count(),

            'total_open_baskets': self.get_open_baskets().count(),

            'total_orders': orders.count(),

            'order_vendor_count': order_vendor_count,

            'total_lines': Line.objects.count(),

            'total_revenue': orders.aggregate(
                Sum('total_incl_tax')
            )['total_incl_tax__sum'] or D('0.00'),

            'orders_line_total': orders_line_total.aggregate(Sum('line_price_incl_tax')),

            'orders_last_day_vendor': orders_last_day_vendor.aggregate(Sum('line_price_incl_tax')),

            'orders_last_day_avg_vendor': orders_last_day_vendor.aggregate(Avg('line_price_incl_tax')),

            'order_status_breakdown': orders.order_by(
                'status'
            ).values('status').annotate(freq=Count('id'))
        }
        return stats

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_stats())
        ctx.update(self.get_vendor())
        return ctx


class CustomCategoryListView(CategoryListView):
    """
    Oscar extended method to view category list.
    """

    table_class = CustomCategoryTable

    def get_queryset(self):
        return Category.get_root_nodes()


@method_decorator(decor.check_is_superuser, name='dispatch')
class ArrangeCategory(generic.View):
    template_name = 'dashboard/catalogue/arrange_category.html'

    def get(self, request, *args, **kwargs):

        context = {}
        category = Category.objects.filter(depth=1).order_by('master_sequence', 'path')

        context['categories'] = category

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form_data = request.POST

        if form_data.get('category_id') is None:
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard/catalogue/categories/')

        try:

            category = Category.objects.filter(depth=1).order_by('path')
            category_array = form_data.get('category_id')
            category_list = category_array.split(',')

            count = 0
            for category in category_list:
                count = count + 1
                Category.objects.filter(id=category).update(master_sequence=count)

            messages.success(self.request, 'Category sequence updated successfully.')
            return redirect('/dashboard/catalogue/categories/')

        except:

            messages.error(self.request, 'Something went wrong.')
            return redirect('/dashboard/catalogue/categories/')

        #
        # category = Category.objects.filter(depth=1).order_by('path')
        # category_array = form_data.get('category_id')
        # category_list = category_array.split(',')
        #
        # alph_number = list(range(10)) + [chr(x) for x in range(65, 91)]
        # unique_sequence = list(itertools.product(alph_number, alph_number, alph_number, alph_number))
        #
        # new_seq_list = []
        # for seq in unique_sequence[:len(category_list) + 1]:
        #     my_string = str(seq[0]) + '' + str(seq[1]) + '' + str(seq[2]) + '' + str(seq[3])
        #     if str(seq[0]) + '' + str(seq[1]) + '' + str(seq[2]) + '' + str(seq[3]) != '0000':
        #         new_seq_list.append(my_string)
        #
        # new_dict = {}
        # for key in category_list:
        #     for value in new_seq_list:
        #         new_dict[key] = value
        #         new_seq_list.remove(value)
        #         break
        #
        # old_paths = []
        # for old_path in category:
        #     old_path_dict = {}
        #     old_path_dict['id'] = old_path.id
        #     old_path_dict['path'] = old_path.path
        #     old_paths.append(old_path_dict)
        #
        # return HttpResponse(category_list)


@method_decorator(decor.check_is_superuser, name='dispatch')
class ArrangeSubCategory(generic.View):
    """
    Method to update category sequence.
    """

    template_name = 'dashboard/catalogue/arrange_sub_category.html'

    def get(self, request, *args, **kwargs):

        context = {}

        if not kwargs.get('pk'):
            messages.error(request, 'Invalid request.')
            return redirect('/dashboard')

        pk = kwargs.get('pk')
        category = None

        try:
            category = Category.objects.get(id=pk, depth=1)
        except:
            messages.error(request, 'Invalid category.')
            return redirect('/dashboard')

        context['main_category'] = category
        context['main_childs'] = category.get_children().order_by('path')

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')
            form_data = request.POST
            category = Category.objects.get(id=pk)

            if form_data.get('category_id') is None:
                messages.error(request, 'Something went wrong.')
                return redirect('/dashboard/catalogue/categories/')

            sub_category_array = form_data.get('category_id')
            sub_category_list = sub_category_array.split(',')

            alph_number = list(range(10)) + [chr(x) for x in range(65, 91)]
            unique_sequence = list(itertools.product(alph_number, alph_number, alph_number, alph_number))

            new_seq_list = []
            for seq in unique_sequence[:len(sub_category_list) + 1]:
                my_string = category.path + '' + str(seq[0]) + '' + str(seq[1]) + '' + str(seq[2]) + '' + str(seq[3])
                if str(seq[0]) + '' + str(seq[1]) + '' + str(seq[2]) + '' + str(seq[3]) != '0000':
                    new_seq_list.append(my_string)

            new_dict = {}
            for key in sub_category_list:
                for value in new_seq_list:
                    new_dict[key] = value
                    new_seq_list.remove(value)
                    break

            old_paths = []
            for old_path in category.get_children():
                old_path_dict = {}
                old_path_dict['id'] = old_path.id
                old_path_dict['path'] = old_path.path
                old_paths.append(old_path_dict)

            # empty old paths

            for id, path in new_dict.items():
                Category.objects.filter(id=id).update(path=random.randint(1000, 100000))

            for id_set, path_set in new_dict.items():
                try:
                    Category.objects.filter(id=id_set).update(path=path_set)
                except:
                    return self.retrive_ids(old_paths)

            messages.success(self.request, 'Category sequence updated successfully..')
            return redirect('/dashboard/catalogue/categories/')

        except Exception as e:

            messages.error(self.request, 'Something went wrong.')
            return redirect('/dashboard/catalogue/categories/')

    def retrive_ids(self, old_paths):

        for old in old_paths:
            Category.objects.filter(id=old['id']).update(path=old['path'])

        messages.error(self.request, 'Something went wrong.')
        return redirect('/dashboard/catalogue/categories/')


@method_decorator(decor.check_is_superuser, name='dispatch')
class ProductUnitListView(generic.ListView):
    """
    Product unit list view.
    """

    template_name = 'dashboard/catalogue/product_unit_list.html'
    queryset = ProductUnit.objects.all().order_by('-id')
    context_object_name = 'product_units'
    form_class = ProductUnitSearchForm
    model = ProductUnit

    def get_queryset(self):

        qs = self.model._default_manager.all()
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data.get('unit'):
            qs = qs.filter(unit__icontains=data.get('unit'))

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(ProductUnitListView, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx


@method_decorator(decor.check_is_superuser, name='dispatch')
class ProductUnitCreateView(generic.FormView):
    """
    Method to store new unit
    """

    template_name = 'dashboard/catalogue/product_unit_create.html'
    form_class = ProductUnitModelForm
    context_object_name = 'form'

    def form_valid(self, form):

        try:
            base_form = form.save(commit=False)
            base_form.save()
            messages.success(self.request, 'New unit created successfully.')
        except:
            messages.error(self.request, 'Something went wrong.')

        return redirect('dashboard:product_unit')


@method_decorator(decor.check_is_superuser, name='dispatch')
class ProductUnitUpdateView(generic.UpdateView):
    model = ProductUnit
    form_class = ProductUnitUpdateModelForm
    template_name = 'dashboard/catalogue/product_unit_update.html'
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        base_form = form.save(commit=False)
        base_form.save()

        messages.success(self.request, 'Unit updated successfully')
        return redirect('dashboard:product_unit')


@method_decorator(decor.check_is_superuser, name='dispatch')
class ProductUnitDeleteView(generic.View):
    """
    Class method to delete
    """

    template_name = 'dashboard/catalogue/product_unit_delete.html'

    def get(self, request, *args, **kwargs):

        if not self.request.user.is_superuser:
            messages.error(self.request, 'Invalid request')
            return redirect('/dashboard')

        try:
            pk = kwargs.get('pk')
            unit = ProductUnit.objects.get(id=pk)

            context = {
                'pk': pk,
                'unit': unit
            }

            return render(request, self.template_name, context=context)
        except Exception as e:
            messages.error(request, 'Invalid request')
            return redirect('/dashboard')

    def post(self, request, *args, **kwargs):

        if not self.request.user.is_superuser:
            messages.error(self.request, 'Invalid request')
            return redirect('/dashboard')

        try:

            pk = request.POST.get('pk')
            ProductUnit.objects.get(id=pk)
            ProductUnit.objects.get(id=pk).delete()

            messages.success(request, 'Unit delete successfully.')

        except:

            messages.error(request, 'Something went wrong.')

        return redirect('dashboard:product_unit')


@method_decorator(decor.check_is_superuser, name='dispatch')
class ProductTypeUpdateView(generic.View):
    """
    Method to update product- product type.
    """

    template_name = 'dashboard/catalogue/product_type_update.html'
    form_class = ProductTypeUpdateForm

    def get(self, request, *args, **kwargs):

        context = {}

        try:

            pk = kwargs.get('pk')
            product = Product.objects.get(id=pk)

            context['pk'] = pk
            context['product'] = product
            context['form'] = self.form_class(instance=product)

        except:

            messages.error(self.request, 'Something went wrong.')
            return redirect('/dashboard')

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        instance = Product.objects.get(id=kwargs.get('pk'))
        form = self.form_class(self.request.POST, instance=instance)

        if not form.is_valid():
            return self.is_invalid(form, instance)
        return self.is_valid(form, pk)

    def is_valid(self, form, pk):

        try:
            base_form = form.save(commit=False)
            base_form.save()
            messages.success(self.request, 'Product type updated successfully.')
            return redirect('/dashboard/catalogue/products/' + str(pk))

        except Exception as e:

            messages.error(self.request, 'Something went wrong.')
            return redirect('/dashboard')

    def is_invalid(self, form, instance):
        context = {
            'form': form,
            'pk': self.kwargs.get('pk'),
            'product': instance
        }
        return render(self.request, self.template_name, context=context)


class CustomProductCreateUpdateView(ProductCreateUpdateView):
    model = Product
    context_object_name = 'product'

    form_class = ProductFormClass
    category_formset = CustProductCategoryFormSet

    image_formset = CustProductImageFormSet
    attribute_formset = AttributeFormSet
    recommendations_formset = ProductRecommendationFormSet
    stockrecord_formset = CustomStockRecordFormSet

    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {'category_formset': self.category_formset,
                         'image_formset': self.image_formset,
                         'attribute_formset': self.attribute_formset,
                         'recommended_formset': self.recommendations_formset,
                         'stockrecord_formset': self.stockrecord_formset}

    def dispatch(self, request, *args, **kwargs):
        resp = super(ProductCreateUpdateView, self).dispatch(
            request, *args, **kwargs)
        return self.check_objects_or_redirect() or resp

    def check_objects_or_redirect(self):
        """
        Allows checking the objects fetched by get_object and redirect
        if they don't satisfy our needs.
        Is used to redirect when create a new variant and the specified
        parent product can't actually be turned into a parent product.
        """
        if self.creating and self.parent is not None:
            is_valid, reason = self.parent.can_be_parent(give_reason=True)
            if not is_valid:
                messages.error(self.request, reason)
                return redirect('dashboard:catalogue-product-list')

    def get_queryset(self):
        """
        Filter products that the user doesn't have permission to update
        """
        return filter_products(Product.objects.all(), self.request.user)

    def get_object(self, queryset=None):
        """
        This parts allows generic.UpdateView to handle creating products as
        well. The only distinction between an UpdateView and a CreateView
        is that self.object is None. We emulate this behavior.

        This method is also responsible for setting self.product_class and
        self.parent.
        """
        self.creating = 'pk' not in self.kwargs

        if self.creating:
            # Specifying a parent product is only done when creating a child
            # product.
            parent_pk = self.kwargs.get('parent_pk')

            if parent_pk is None:
                self.parent = None
                # A product class needs to be specified when creating a
                # standalone product.
                product_class_slug = self.kwargs.get('product_class_slug')
                self.product_class = get_object_or_404(
                    ProductClass, slug=product_class_slug)
            else:
                self.parent = get_object_or_404(Product, pk=parent_pk)
                self.product_class = self.parent.product_class

            return None  # success
        else:
            if self.request.user.is_superuser:
                product = super(ProductCreateUpdateView, self).get_object(queryset)
                self.product_class = product.get_product_class()
                self.parent = product.parent
                return product
            else:

                partner_obj = Partner.objects.get(users=self.request.user)
                stock_record = StockRecord.objects.filter(partner=partner_obj.id).values_list('product', flat=True)

                product = super(ProductCreateUpdateView, self).get_object(queryset)

                if product.id in stock_record:
                    self.product_class = product.get_product_class()
                    self.parent = product.parent
                    return product
                else:
                    raise PermissionDenied

    def get_vendor(self):
        isVendor = self.request.user.groups.filter(name='Vendor').exists()
        vendor_obj = {
            'isVendor': isVendor,
        }
        return vendor_obj

    def check_rate_card_product(self):
        price = None
        if self.object:
            if self.object.product_cost_type == "Multiple" and not ProductCostEntries.objects.filter(
                    product=self.object):
                messages.error(self.request,
                               _("Please create rate card entry for this product"))
                return True
            # if self.object.product_cost_type == "Single" and self.object.is_transporation_available:
            #     if self.object.product_class.name in ['Rent', 'Professional']:
            #         price=self.object.stockrecords.all()
            #         if price and not price.last().rent_transportation_price:
            #             messages.error(self.request,
            #                            _("Please enter rent transportation cost"))
            #             return True
            #
            #     elif self.object.product_class.name == 'Sale':
            #         price=self.object.stockrecords.all()
            #         if price and not price.last().sale_transportation_price:
            #             messages.error(self.request,
            #                            _("Please enter sale transportation cost"))
            #             return True
            #
            #     elif self.object.product_class.name == 'Rent Or Sale':
            #         price=self.object.stockrecords.all()
            #         if price:
            #             price = price.last()
            #             if not price.rent_transportation_price and not price.sale_transportation_price:
            #                 messages.error(self.request,
            #                                _("Please enter rent and sale transportation cost"))
            #                 return True
            #             elif not price.rent_transportation_price and price.sale_transportation_price:
            #                 messages.error(self.request,
            #                                _("Please enter rent transportation cost"))
            #                 return True
            #             elif price.rent_transportation_price and not price.sale_transportation_price:
            #                 messages.error(self.request,
            #                                _("Please enter sale transportation cost"))
            #                 return True
            return False

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreateUpdateView, self).get_context_data(**kwargs)
        ctx['product_class'] = self.product_class
        ctx['parent'] = self.parent
        ctx['title'] = self.get_page_title()
        ctx['rate_product'] = self.check_rate_card_product()
        ctx.update(self.get_vendor())

        for ctx_name, formset_class in self.formsets.items():

            if ctx_name not in ctx:
                if ctx_name == 'attribute_formset':
                    obj = Attribute_Mapping.objects.filter(product=self.object)
                    context = {
                        'pk': obj.distinct('attribute').values('pk'),
                        'attribute': obj.distinct('attribute'),
                        'value': obj.distinct('value')

                    }
                    ctx[ctx_name] = formset_class(self.product_class,
                                                  self.request.user,
                                                  instance=self.object)

                else:
                    ctx[ctx_name] = formset_class(self.product_class,
                                                  self.request.user,
                                                  instance=self.object)
        return ctx

    def get_page_title(self):
        if self.creating:
            if self.parent is None:
                return _('Create new %(product_class)s product') % {
                    'product_class': self.product_class.name}
            else:
                return _('Create new variant of %(parent_product)s') % {
                    'parent_product': self.parent.title}
        else:
            if self.object.title or not self.parent:
                return self.object.title
            else:
                return _('Editing variant of %(parent_product)s') % {
                    'parent_product': self.parent.title}

    def get_form_kwargs(self):
        kwargs = super(ProductCreateUpdateView, self).get_form_kwargs()
        kwargs['product_class'] = self.product_class
        kwargs['parent'] = self.parent
        return kwargs

    def process_all_forms(self, form):
        """
        Short-circuits the regular logic to have one place to have our
        logic to check all forms
        """
        # Need to create the product here because the inline forms need it
        # can't use commit=False because ProductForm does not support it
        if self.creating and form.is_valid():
            self.object = form.save()

        formsets = {}
        for ctx_name, formset_class in self.formsets.items():
            if ctx_name == "attribute_formset":
                attribute_formset = formset_class(self.product_class,
                                                  self.request.user,
                                                  self.request.POST,
                                                  self.request.FILES,
                                                  instance=self.object)

            formsets[ctx_name] = formset_class(self.product_class,
                                               self.request.user,
                                               self.request.POST,
                                               self.request.FILES,
                                               instance=self.object)
        for formset in formsets.values():
            print(formset.errors)
        is_valid = form.is_valid() and all([formset.is_valid() for formset in formsets.values()])

        cross_form_validation_result = self.clean(form, formsets)

        if is_valid and cross_form_validation_result:
            return self.forms_valid(form, formsets)
        else:
            return self.forms_invalid(form, formsets)

    # form_valid and form_invalid are called depending on the validation result
    # of just the product form and redisplay the form respectively return a
    # redirect to the success URL. In both cases we need to check our formsets
    # as well, so both methods do the same. process_all_forms then calls
    # forms_valid or forms_invalid respectively, which do the redisplay or
    # redirect.
    form_valid = form_invalid = process_all_forms

    def clean(self, form, formsets):
        """
        Perform any cross-form/formset validation. If there are errors, attach
        errors to a form or a form field so that they are displayed to the user
        and return False. If everything is valid, return True. This method will
        be called regardless of whether the individual forms are valid.
        """
        return True

    def forms_valid(self, form, formsets):
        """
        Save all changes and display a success url.
        When creating the first child product, this method also sets the new
        parent's structure accordingly.
        """
        if self.creating:
            self.handle_adding_child(self.parent)
        else:
            # a just created product was already saved in process_all_forms()
            self.object = form.save()

        # Save formsets
        for formset_key, formset in formsets.items():
            try:
                if formset_key == 'attribute_formset':
                    self.save_product_attribute(formset)
                    print("#######", self.object.attribute_mapping.all())
                    continue

                formset.save()
            except Exception as e:

                import os
                import sys
                print('-----------in exception----------')
                print(e.args)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        return HttpResponseRedirect(self.get_success_url())

    def save_product_attribute(self, formsets):
        for formset in formsets:
            attribute_values = formset.cleaned_data.get('value')
            attr = formset.cleaned_data.get('attribute')
            if attribute_values and attr:
                attr_obj = Attribute_Mapping.objects.filter(
                    product=self.object,
                    attribute=formset.cleaned_data.get('attribute')
                )
                if attr_obj:
                    Attribute_Mapping.objects.filter(
                        product=self.object,
                        attribute=formset.cleaned_data.get('attribute')
                    ).update(value=attribute_values)
                else:
                    Attribute_Mapping.objects.create(
                        product=self.object,
                        attribute=formset.cleaned_data.get('attribute'),
                        value=attribute_values
                    )

    def handle_adding_child(self, parent):
        """
        When creating the first child product, the parent product needs
        to be implicitly converted from a standalone product to a
        parent product.
        """
        # ProductForm eagerly sets the future parent's structure to PARENT to
        # pass validation, but it's not persisted in the database. We ensure
        # it's persisted by calling save()
        if parent is not None:
            parent.structure = Product.PARENT
            parent.save()

    def forms_invalid(self, form, formsets):
        # delete the temporary product again
        if self.creating and self.object and self.object.pk is not None:
            self.object.delete()
            self.object = None

        messages.error(self.request,
                       _("Your submitted data was not valid - please "
                         "correct the errors below"))
        ctx = self.get_context_data(form=form, **formsets)
        return self.render_to_response(ctx)

    def get_url_with_querystring(self, url):
        url_parts = [url]
        if self.request.GET.urlencode():
            url_parts += [self.request.GET.urlencode()]
        return "?".join(url_parts)

    def get_success_url(self):
        """
        Renders a success message and redirects depending on the button:
        - Standard case is pressing "Save"; redirects to the product list
        - When "Save and continue" is pressed, we stay on the same page
        - When "Create (another) child product" is pressed, it redirects
          to a new product creation page
        """
        msg = render_to_string(
            'dashboard/catalogue/messages/product_saved.html',
            {
                'product': self.object,
                'creating': self.creating,
                'request': self.request
            })
        messages.success(self.request, msg, extra_tags="safe noicon")

        action = self.request.POST.get('action')
        if action == 'continue':
            url = reverse(
                'dashboard:catalogue-product', kwargs={"pk": self.object.id})
        elif action == 'create-another-child' and self.parent:
            url = reverse(
                'dashboard:catalogue-product-create-child',
                kwargs={'parent_pk': self.parent.pk})
        elif action == 'create-child':
            url = reverse(
                'dashboard:catalogue-product-create-child',
                kwargs={'parent_pk': self.object.pk})
        else:
            url = reverse('dashboard:catalogue-product-list')
        return self.get_url_with_querystring(url)


@csrf_exempt
def delete_combo_product(request):
    """
        Ajax method to delete product image.
        """

    if request.is_ajax():

        combo_id = request.GET.get('combo_id')

        if not combo_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        if not ComboProducts.objects.filter(id=combo_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        ComboProducts.objects.filter(id=combo_id).delete()
        messages.success(request, 'Product removed successfully.')
        return HttpResponse('TRUE')

    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_product_image(request):
    """
    Ajax method to delete product image.FilteredProductListView
    """

    if request.is_ajax():

        image_id = request.GET.get('image_id')

        if not image_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        if not ProductImage.objects.filter(id=image_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        ProductImage.objects.filter(id=image_id).delete()
        messages.success(request, 'Image deleted successfully.')
        return HttpResponse('200')

    return HttpResponse('503')


@csrf_exempt
def delete_product_attribute(request):
    """
    Ajax method to delete product image.FilteredProductListView
    """

    if request.is_ajax():
        attribute_id = request.GET.get('attribute_id')

        if not attribute_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        if not Attribute_Mapping.objects.filter(id=attribute_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        obj = Attribute_Mapping.objects.filter(id=attribute_id).delete()
        messages.success(request, 'Attribute deleted successfully.')
        return HttpResponse('200')

    return HttpResponse('503')


@csrf_exempt
def get_values_of_attribute(request):
    """
       Ajax method to delete product image.FilteredProductListView
       """

    if request.is_ajax():
        attribute_id = request.GET.get('attribute_id')

        if not attribute_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        if not Attribute.objects.filter(id=attribute_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        obj = Attribute.objects.filter(id=attribute_id)
        obj1 = Attribute.objects.filter(attribute=obj.last().attribute)
        if obj1:
            return render(request, 'admin/partials/values_dropdown.html', {'prods': obj1})

    return HttpResponse('503')


@csrf_exempt
def delete_bulk_combo_data(request):
    """
    Ajax method to delete bulk combo.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        combo_id = request.GET.get('combo_id')

        if not combo_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        combo_list = combo_id.split(',')

        # check all ids are valid
        try:
            for combo in combo_list:
                Product.objects.get(id=combo)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Product.objects.filter(id__in=combo_list).delete()

        _pr_str = 'combo'
        if len(combo_list) > 1:
            _pr_str = 'combos'

        success_str = 'Total %s %s deleted successfully.' % (len(combo_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_event(request):
    """
    Ajax method to delete bulk event.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        ev_ids = request.GET.get('ev_id')

        if not ev_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        ev_list = ev_ids.split(',')

        # check all ids are valid
        try:
            for ev in ev_list:
                _VendorCalender.objects.get(id=ev)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        _VendorCalender.objects.filter(id__in=ev_list).delete()

        _pr_str = 'event'
        if len(ev_list) > 1:
            _pr_str = 'events'

        success_str = 'Total %s %s deleted successfully.' % (len(ev_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_coupon(request):
    """
    Ajax method to delete bulk coupon.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        coupon_ids = request.GET.get('coupon_id')

        if not coupon_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        coupon_list = coupon_ids.split(',')

        # check all ids are valid
        try:
            for coupon in coupon_list:
                Voucher.objects.get(id=coupon)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        if coupon_list:
            v_obj = Voucher.objects.filter(id__in=coupon_list)
            c_obj = CustomizeCouponModel.objects.filter(voucher__in=v_obj).values_list('range__id', flat= True)
            r_obj = Range.objects.filter(id__in=c_obj).values_list('id', flat=True)
            r_obj1 = Range.objects.filter(id__in=c_obj)
            Range.objects.filter(id__in=r_obj1).delete()
            Benefit.objects.filter(range__id__in=r_obj).delete()
            CustomizeCouponModel.objects.filter(voucher__in=v_obj).delete()

        Voucher.objects.filter(id__in=coupon_list).delete()

        _pr_str = 'coupon'
        if len(coupon_list) > 1:
            _pr_str = 'coupons'

        success_str = 'Total %s %s deleted successfully.' % (len(coupon_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_season(request):
    """
    Ajax method to delete bulk coupon season.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        season_ids = request.GET.get('season_id')

        if not season_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        season_list = season_ids.split(',')

        # check all ids are valid
        try:
            for season in season_list:
                Range.objects.get(id=season)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Range.objects.filter(id__in=season_list).delete()

        _pr_str = 'coupon season'
        if len(season_list) > 1:
            _pr_str = 'coupon seasons'

        success_str = 'Total %s %s deleted successfully.' % (len(season_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_reviews(request):
    """
    Ajax method to delete bulk reviews.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        review_ids = request.GET.get('review_id')

        if not review_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        review_list = review_ids.split(',')

        # check all ids are valid
        try:
            for review in review_list:
                try:
                    ProductReview.objects.get(id=review).delete()
                except:
                    continue
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        # ProductReview.objects.filter(id__in=review_list).delete()

        _pr_str = 'review'
        if len(review_list) > 1:
            _pr_str = 'reviews'

        success_str = 'Total %s %s deleted successfully.' % (len(review_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_category(request):
    """
    Ajax method to delete bulk categories.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        category_ids = request.GET.get('category_id')

        if not category_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        category_list = category_ids.split(',')

        # check all ids are valid
        try:
            for category in category_list:
                Category.objects.get(id=category)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Category.objects.filter(id__in=category_list).delete()

        _pr_str = 'category'
        if len(category_list) > 1:
            _pr_str = 'categories'

        success_str = 'Total %s %s deleted successfully.' % (len(category_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_user(request):
    """
    Ajax method to delete end user
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        user_ids = request.GET.get('user_id')

        if not user_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        user_list = user_ids.split(',')

        # check all ids are valid
        try:
            for user in user_list:
                User.objects.get(id=user)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        User.objects.filter(id__in=user_list).delete()

        _pr_str = 'user'
        if len(user_list) > 1:
            _pr_str = 'users'

        success_str = 'Total %s %s deleted successfully.' % (len(user_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_vendor(request):
    """
    Ajax method to delete vendor
    """

    if request.is_ajax():

        vendor_ids = request.GET.get('vendor_id')

        if not vendor_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        vendor_list = vendor_ids.split(',')

        # check all ids are valid
        try:
            for vendor in vendor_list:
                Partner.objects.get(id=vendor)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')
        for vendor in vendor_list:
            qs = Product.objects.all()
            part_obj = Partner.objects.filter(id=vendor)
            qs_obj = qs.filter(stockrecords__partner=part_obj.last()).update(is_deleted=True)

            User.objects.filter(id=part_obj.last().users.last().id).delete()

        Partner.objects.filter(id__in=vendor_list).delete()

        _pr_str = 'vendor'
        if len(vendor_list) > 1:
            _pr_str = 'vendors'

        success_str = 'Total %s %s deleted successfully.' % (len(vendor_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_units(request):
    """
    Ajax method to delete vendor
    """

    if request.is_ajax():

        unit_ids = request.GET.get('unit_id')

        if not unit_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        unit_list = unit_ids.split(',')

        # check all ids are valid
        try:
            for unit in unit_list:
                ProductUnit.objects.get(id=unit)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        ProductUnit.objects.filter(id__in=unit_list).delete()

        _pr_str = 'unit'
        if len(unit_list) > 1:
            _pr_str = 'units'

        success_str = 'Total %s %s deleted successfully.' % (len(unit_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_product(request):
    """
    Ajax method to delete products
    """

    if request.is_ajax():

        product_ids = request.GET.get('product_id')

        if not product_ids:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        product_list = product_ids.split(',')

        # check all ids are valid
        try:
            for product in product_list:
                Product.objects.get(id=product)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Product.objects.filter(id__in=product_list).delete()

        _pr_str = 'product'
        if len(product_list) > 1:
            _pr_str = 'products'

        success_str = 'Total %s %s deleted successfully.' % (len(product_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def update_product(request):
    """
    Ajax method to update products
    """

    if request.is_ajax():

        product_ids = request.GET.get('product_id')
        status = request.GET.get('status')

        if not product_ids or not status:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        product_list = product_ids.split(',')

        # check all ids are valid
        try:
            for product in product_list:
                Product.objects.get(id=product)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Product.objects.filter(id__in=product_list, is_deleted=False).update(is_approved=status)

        _pr_str = 'product'
        if len(product_list) > 1:
            _pr_str = 'products'

        success_str = 'Total %s %s updated successfully.' % (len(product_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


partner = get_model('partner', 'partner')

######################################################
# Report function #
######################################################


from oscar.apps.dashboard.reports.views import IndexView
from django.http import Http404, HttpResponseForbidden

ReportForm = get_class('dashboard.forms', 'CustomReportForm')
GeneratorRepository = get_class('dashboard.utils', 'GeneratorRepository')


######################################################
# partner
######################################################


class CustomPartnerListView(PartnerListView):
    """
    Vendor list view.
    """

    model = Partner
    context_object_name = 'partners'
    template_name = 'dashboard/partners/partner_list.html'
    form_class = VendorStatusSearchForm_c
    paginate_by = 20

    def get_queryset(self):

        # main query
        qs = self.model._default_manager.all()
        qs = sort_queryset(qs, self.request, ['name'])

        self.description = _("All partners")
        self.is_filtered = False

        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['status']:
            js = Partner.objects.all().values_list('users')
            xs = User.objects.filter(id__in=js, is_active=data['status']).values_list('id')
            qs = qs.filter(users__in=xs)

        if data.get('pincode'):
            qs = qs.filter(pincode__icontains=data.get('pincode'))

        if data.get('search_type') and data.get('all_search'):

            search_text = data.get('all_search')
            search_type = data.get('search_type')

            if search_type == '1':  # by vendor name
                qs = qs.filter(name__icontains=search_text)

            if search_type == '2':  # by vendor email
                qs = qs.filter(email_id__icontains=search_text)

            if search_type == '3':  # by business name
                qs = qs.filter(business_name__icontains=search_text)

            if search_type == '4':  # by pin code
                qs = qs.filter(pincode__icontains=search_text)

            if search_type == '5':  # by phone number
                qs = qs.filter(
                    Q(telephone_number__icontains=search_text) | Q(alternate_mobile_number__icontains=search_text)
                )

        self.vendor_obj = qs
        return qs

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['queryset_description'] = self.description
        ctx['form'] = self.form
        ctx['is_filtered'] = self.is_filtered

        return ctx


class CustomPartnerManageView(generic.UpdateView):
    """
    Vendor manage/update view.
    """

    template_name = 'dashboard/partners/partner_manage.html'
    form_class = PartnerUpdateForm

    success_url = reverse_lazy('dashboard:partner-list')

    def get_object(self, queryset=None):

        self.partner = get_object_or_404(Partner, pk=self.kwargs['pk'])
        self.user = self.partner.users.all()

        return self.partner

    def get_initial(self):

        country = 1
        partner_obj = Partner.objects.get(id=self.partner.id)

        return {
            'name': self.partner.name,
            'address_line_1': self.partner.address_line_1,
            'address_line_2': self.partner.address_line_2,
            'telephone_number': self.partner.telephone_number,
            'email_id': self.partner.email_id,
            'country': country,
            'state': self.partner.state_id,
            'city': self.partner.city_id,
            'pincode': self.partner.pincode,
            'categories': partner_obj.categories,
            'business_name': self.partner.business_name,
            'alternate_mobile_number': self.partner.alternate_mobile_number,
        }

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['partner'] = self.partner
        ctx['title'] = self.partner.name

        self.user = self.partner.users.all()

        for vendorUser in self.user:
            if vendorUser.is_active:
                ctx['userIsActive'] = True
            else:
                ctx['userIsActive'] = False

        ctx['users'] = self.partner.users.all()

        return ctx

    def form_valid(self, form):

        messages.success(self.request, _("Partner '%s' was updated successfully.") % self.partner.name)

        self.partner.name = form.cleaned_data['name']
        is_active = form.cleaned_data['user_active']

        user_update_obj = User.objects.get(id__in=self.user)
        user_update_obj.is_active = is_active
        user_update_obj.email = form.cleaned_data['email_id']
        user_update_obj.username = form.cleaned_data['email_id']
        user_update_obj.save()

        if user_update_obj.is_active == True and not self.partner.updated_date:
            try:

                current_site = Site.objects.get_current()
                mail_subject = 'TakeRentPe - ASP Account Activation.'
                message = render_to_string(
                    'customer/emails/thank_you_email.html',
                    {
                        'vendor': user_update_obj,
                        'email_id': user_update_obj.email,
                        'domain': current_site.domain,
                    }
                )

                to_email = user_update_obj.email
                from_email = settings.FROM_EMAIL_ADDRESS
                email = EmailMessage(mail_subject, message, from_email, [to_email])
                email.content_subtype = "html"
                email.send()

                # send sms code WELCOME & SMS ID VERIFICATION SMS
                message = 'Welcome to the family ' + str(user_update_obj.first_name) + ' Thank you for being an ASP with our Family. We’ll always look forward for amazing things in future! Happy celebranto, Take Rent Pe'
                msg_kwargs = {
                    'message': message,
                    'mobile_number': self.partner.telephone_number,
                }
                print('send wel for asp##########')
                send_sms(**msg_kwargs)
                print('send wel for asp##########')


            except:
                pass

        self.partner.updated_date = datetime.datetime.now()

        qs = Product.objects.all()
        partner_obj = partner.objects.get(users=user_update_obj)
        if not user_update_obj.is_active:
            qs_obj = qs.filter(stockrecords__partner=partner_obj).update(is_approved='Pending')
        self.partner.save()
        return super().form_valid(form)


class VendorCalenderListView(generic.View):
    """
    View to display vendor calender.
    """

    template_name = 'dashboard/vendor/calender/calender_list.html'
    model = _VendorCalender

    def get(self, request, *args, **kwargs):

        context = dict()

        try:

            user = request.user

            # get notes
            notes_list = []
            notes = Notes.objects.all()

            if notes:
                for note in notes:
                    notes_list.append(
                        {
                            'title': 'Notes :' + note.note,
                            'start': str(note.start_date.date()),

                        }
                    )

            # get events
            events_list = []
            events = _VendorCalender.objects.all()

            if user.is_staff and not user.is_superuser:
                vendor = Partner.objects.filter(users=user)
                events = events.filter(vendor=vendor.last())

            for event in events:
                event_end_date = ''
                if event.to_date:
                    event_end_date = str(event.to_date.date() + datetime.timedelta(days=1))
                events_list.append(
                    {
                        'title': 'Booked :' + event.product.title,
                        'start': str(event.from_date.date()),
                        'end': event_end_date,
                    }
                )

            context['notes'] = json.dumps(notes_list)
            context['events'] = json.dumps(events_list)

            return render(self.request, self.template_name, context=context)

        except Exception as e:
            messages.error(self.request, 'Something went wrong.')
            return redirect('/dashboard/')


def admin_notes(request):
    notes_obj = Notes.objects.all()
    evnt = []
    _calendar_list = []
    try:
        if notes_obj:
            _calendar_list.clear()
            events = {}

            for i in notes_obj:
                _calendar_list.append(
                    {
                        'title': 'Notes :' + i.note,
                        'start': str(i.start_date.date()),

                    }
                )

    except Exception as e:
        import sys
        import os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        evnt = ""

    json_string = json.dumps(_calendar_list),

    return HttpResponse(json_string)


class VendorCalendarEventAddView(generic.View):
    """
    Class to store vendor calendar event.
    """

    template_name = 'dashboard/vendor/calender/calender_event_add.html'
    form_class = VendorCalendarAddEvent

    def get(self, request, *args, **kwargs):

        context = {
            'title': 'Add calendar event',
            'form': self.form_class(request=request)
        }

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST, request=request)

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        try:

            user = User.objects.get(id=self.request.user.id)
            if user.is_staff and user.is_active:
                vendor = Partner.objects.filter(users=user).last()
                base_form = form.save(commit=False)
                base_form.vendor = vendor
                base_form.save()

                messages.success(self.request, 'Record saved successfully.')
                return redirect('dashboard:vendor-calender')

            messages.error(self.request, 'Invalid request.')
            return redirect('/dashboard')

        except Exception as e:

            messages.error(self.request, 'Something went wrong.')
            return redirect('/dashboard')

    def is_invalid(self, form):

        context = {
            'title': 'Add calendar event',
            'form': form
        }

        messages.error(self.request, 'Please enter valid data.')
        return render(self.request, self.template_name, context=context)


class VendorCalendarTableView(generic.ListView):
    """
    Method to view vendor calendar.
    """

    template_name = 'dashboard/vendor/calender/calender_table_list.html'
    context_object_name = 'calendars'
    model = _VendorCalender
    queryset = _VendorCalender.objects.all()
    form_class = dash_form.VendorCalenderSearchForm

    def get_queryset(self):

        """
        Return vendor wise queryset
        :return: queryset
        """

        data = self.request.GET
        user = self.request.user

        if user.is_superuser:
            queryset = self.model.objects.filter(product__is_deleted=False)
        else:
            partner = Partner.objects.get(users=user)
            queryset = self.model.objects.filter(vendor=partner, product__is_deleted=False)

        if data.get('product'):
            product = data.get('product')
            queryset = queryset.filter(product=product)

        if data.get('category') and data.get('sub_category'):
            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            queryset = queryset.filter(product__categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            queryset = queryset.filter(product__categories__in=id_list)
            # queryset = queryset.filter(product__categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            queryset = queryset.filter(product__categories__in=category.values_list('id', flat=True))

        return queryset

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(user=self.request.user, data=self.request.GET)
        return ctx


class VendorCalendarEditForm(generic.View):
    template_name = 'dashboard/vendor/calender/calender_table_update.html'
    form_class = VendorCalendarAddEvent

    def get(self, request, *args, **kwargs):

        pk = kwargs['pk']
        user = User.objects.get(id=request.user.id)
        if user.is_staff and user.is_active:
            vendor = Partner.objects.filter(users=user).last()
            try:
                event = _VendorCalender.objects.get(id=pk, vendor=vendor)
                form = self.form_class(instance=event, request=request)
            except:
                messages.error(request, 'Invalid request.')
                return redirect('dashboard:vendor-calender-list')

        else:
            messages.error(request, 'Invalid request.')
            return redirect('dashboard:vendor-calender-list')

        context = {
            'form': form
        }

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs['pk']
        user = User.objects.get(id=request.user.id)
        if user.is_staff and user.is_active:
            vendor = Partner.objects.filter(users=user).last()
            try:
                event = _VendorCalender.objects.get(id=pk, vendor=vendor)
                form = self.form_class(request.POST, instance=event, request=request)
                if form.is_valid() is False:
                    return self.is_invalid(form)
                return self.is_valid(form)
            except:
                messages.error(request, 'Invalid request.')
                return redirect('dashboard:vendor-calender-list')

        else:
            messages.error(request, 'Invalid request.')
            return redirect('dashboard:vendor-calender-list')

    def is_valid(self, form):
        base_form = form.save(commit=False)
        base_form.save()
        messages.success(self.request, 'Record updated successfully.')
        return redirect('dashboard:vendor-calender-list')

    def is_invalid(self, form):

        context = {
            'title': 'Add calendar event',
            'form': form
        }

        messages.error(self.request, 'Please enter valid data.')
        return render(self.request, self.template_name, context=context)


class VendorCalendarDeleteView(generic.View):
    """
    View to delete vendor calendar event.
    """

    template_name = 'dashboard/vendor/calender/calender_table_delete.html'

    def get(self, request, *args, **kwargs):

        pk = kwargs['pk']
        user = User.objects.get(id=request.user.id)
        if user.is_active:

            try:
                if user.is_superuser:
                    event = _VendorCalender.objects.get(id=pk)
                else:
                    vendor = Partner.objects.filter(users=user).last()
                    event = _VendorCalender.objects.get(id=pk, vendor=vendor)
            except:
                messages.error(request, 'Invalid request.')
                return redirect('dashboard:vendor-calender-list')

        else:
            messages.error(request, 'Invalid request.')
            return redirect('dashboard:vendor-calender-list')

        context = {
            'event': event
        }

        return render(request, self.template_name, context=context)


class VendorCalendarConfirm(generic.View):

    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs['pk']
            _VendorCalender.objects.filter(id=pk).delete()
            messages.success(self.request, 'Record delete successfully.')
            return redirect('dashboard:vendor-calender-list')

        except:

            messages.error(self.request, 'Something went wrong.')
            return redirect('dashboard:vendor-calender-list')


#################################################
# dashboard category view
#################################################
from oscar.apps.dashboard.catalogue.views import CategoryCreateView, CategoryUpdateView

CustomCategoryForm = get_class('dashboard.forms', 'CustomCategoryForm')


class CustomCategoryCreateView(CategoryCreateView):
    template_name = 'dashboard/catalogue/category_form.html'
    form_class = CustomCategoryForm

    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):
        base_form = form.save(commit=False)
        if form.cleaned_data['show_on_frontside']:
            id = self.request.POST.get('_ref_node_id')
            obj = Category.objects.filter(id=id)
            if obj and not obj.last().show_on_frontside:
                form.cleaned_data['show_on_frontside'] = False

        if form.cleaned_data['show_in'] == '0':
            base_form.sequence = None
            base_form.show_in_icons = None

        base_form.save()

        # form.save()
        messages.success(self.request, 'Category created successfully.')
        return redirect('/dashboard/catalogue/categories/')


class CustomCategoryUpdateView(CategoryUpdateView):
    form_class = CustomCategoryForm

    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):
        base_form = form.save(commit=False)

        if form.cleaned_data['show_in'] == '0':
            base_form.sequence = None
            base_form.show_in_icons = None

        base_form.save()
        # form.save()
        if not form.cleaned_data['show_on_frontside']:
            name = form.cleaned_data['name']
            obj = Category.objects.filter(name=name)
            if obj:
                obj.last().get_descendants().update(show_on_frontside=False)

        messages.success(self.request, 'Category updated successfully.')
        return redirect('/dashboard/catalogue/categories/')


##################################################
# dashboard-user app view
##################################################


class CustomIndexView(UserIndexView):
    """
    Table view of users.
    """

    table_class = UserTable
    form_class = CustomUserSearchForm

    def get_queryset(self):

        """
        Method to return queryset.
        :return: queryset
        """

        queryset = self.model.objects.all().order_by('-date_joined')
        return self.apply_search(queryset)

    def get_table(self, **kwargs):

        """
        Constructor table
        :param kwargs: default
        :return: table object
        """

        table = super().get_table(**kwargs)
        table.caption = self.desc_template % self.desc_ctx

        return table

    def _change_users_active_status(self, users, value):

        """
        Update user active status
        :param users: user list
        :param value: Boolean
        :return: list
        """

        for user in users:
            if not user.is_superuser:
                user.is_active = value
                if value is True:
                    CustomProfile.objects.filter(user=user).update(is_blocked=False)
                else:
                    CustomProfile.objects.filter(user=user).update(is_blocked=True)
                user.save()
        messages.info(self.request, _("Users' status successfully changed"))
        return redirect('dashboard:users-index')

    def apply_search(self, queryset):

        """
        Apply search method
        :param queryset: queryset
        :return: queryset
        """

        self.desc_ctx = {
            'main_filter': _('All users'),
            'email_filter': '',
            'name_filter': '',
        }

        if self.form.is_valid():
            return self.apply_search_filters(queryset, self.form.cleaned_data)
        else:
            return queryset

    def apply_search_filters(self, queryset, data):

        """
        Function is split out to allow customisation with little boilerplate.
        :param queryset: queryset
        :param data: data
        :return: search
        """

        if data['email']:
            email = normalise_email(data['email'])
            queryset = queryset.filter(email__icontains=email)
            self.desc_ctx['email_filter'] \
                = _(" with email matching '%s'") % email

        if data['name']:
            parts = data['name'].split()
            condition = Q()
            for part in parts:
                condition &= Q(first_name__icontains=part) \
                             | Q(last_name__icontains=part)
            queryset = queryset.filter(condition).order_by('first_name').distinct()
            self.desc_ctx['name_filter'] \
                = _(" with name matching '%s'") % data['name']

        if data['status']:
            queryset = queryset.filter(is_active=data['status'])

        return queryset


##################################################
# dashboard-ranges view
##################################################


from oscar.apps.dashboard.ranges.views import RangeUpdateView, RangeListView


class CustomRangeListView(RangeListView):
    """
    Oscar extended range list view
    """

    form_class = dash_form.SeasonSearchForm
    template_name = 'dashboard/ranges/range_list.html'

    def get_queryset(self):
        data = self.request.GET
        queryset = self.model.objects.all()

        if data.get('season_name'):
            season_name = data.get('season_name')
            queryset = queryset.filter(name__icontains=season_name)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Context data method
        :param kwargs: default
        :return: context
        """

        ctx = super(CustomRangeListView, self).get_context_data(**kwargs)

        ctx['form'] = self.form_class
        return ctx


class CustomRangeCreateView(RangeCreateView):
    """
    Oscar extended range create view.
    """

    template_name = 'dashboard/ranges/range_form.html'
    form_class = CustomRangeForm


class CustomRangeUpdateView(RangeUpdateView):
    form_class = CustomRangeForm


##################################################
# dashboard-voucher view
##################################################


class CustomVoucherCreateView(VoucherCreateView):
    """
    Oscar extended voucher create view
    """

    template_name = 'dashboard/vouchers/voucher_form.html'
    form_class = VoucherForm


class CustomVoucherUpdateView(VoucherUpdateView):
    """
    Oscar extended voucher update view
    """

    form_class = VoucherForm


class CustomVoucherDeleteView(VoucherDeleteView):
    """
    Oscar extended voucher delete view.
    """

    def get_success_url(self):
        messages.warning(self.request, _("Voucher deleted"))
        return reverse('dashboard:voucher-list1')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        benefit_list = self.object.offers.values_list('benefit', flat=True)
        range = Benefit.objects.filter(id__in=benefit_list).values_list('range', flat=True)
        Range.objects.filter(id__in=range).delete()
        self.object.delete()

        return HttpResponseRedirect(success_url)


class CustomVoucherListView(VoucherListView):
    """
    Oscar extended voucher list view
    """

    form_class = VoucherSearchForm

    def get_queryset(self):

        """
        method to return queryset.
        :return: queryset
        """

        qs = self.model.objects.all().order_by('-date_created')
        qs = sort_queryset(
            qs, self.request,
            ['num_basket_additions', 'num_orders', 'date_created'], '-date_created'
        )

        self.description_ctx = {
            'main_filter': _('All vouchers'),
            'name_filter': '',
            'code_filter': ''
        }

        # If form not submitted, return early
        is_form_submitted = 'name' in self.request.GET
        if not is_form_submitted:
            self.form = self.form_class()
            return qs.filter(voucher_set__isnull=True)

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data
        if data['name']:
            qs = qs.filter(name__icontains=data['name'])

        if data['code']:
            qs = qs.filter(code__icontains=data['code'])

        if not data['in_set']:
            qs = qs.filter(voucher_set__isnull=True)

        return qs


##################################################
# admin/vendor password change
##################################################
from django.views.generic import View
# PasswordChangeForm = get_class('dashboard.forms', 'CustomVoucherForm')
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from oscar.apps.customer.utils import get_password_reset_url
from django.contrib.auth import update_session_auth_hash

Dispatcher = get_class('customer.utils', 'Dispatcher')
CommunicationEventType = get_model('customer', 'CommunicationEventType')
Notes = get_model('customer', 'Notes')


class AdminChangePassword(generic.FormView):
    form_class = PasswordChangeForm
    template_name = 'FrontendSite/password_change.html'
    communication_type_code = 'PASSWORD_CHANGED'

    success_url = reverse_lazy('dashboard:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, _("Password updated"))

        ctx = {
            'user': self.request.user,
            'site': get_current_site(self.request),
            'reset_url': get_password_reset_url(self.request.user),
        }
        msgs = CommunicationEventType.objects.get_and_render(
            code=self.communication_type_code, context=ctx)
        Dispatcher().dispatch_user_messages(self.request.user, msgs)

        return redirect(self.get_success_url())


def queryset_orders_for_user(user):
    queryset = Order._default_manager.select_related(
        'billing_address', 'billing_address__country',
        'shipping_address', 'shipping_address__country',
        'user'
    ).prefetch_related('lines')

    if not user.is_staff:
        return queryset
    else:
        if user.is_superuser:

            return queryset
        else:
            partners = Partner._default_manager.filter(users=user)
            query_sets = queryset.filter(lines__partner__in=partners).distinct()

            return query_sets


def custom_get_order_for_user_or_404(user, number):
    try:
        # return queryset_orders_for_user(user).get(number=number)
        return queryset_orders_for_user(user).get(number=number)
    except ObjectDoesNotExist:
        raise Http404()


from oscar.apps.dashboard.orders.views import OrderDetailView

#######################################
# low stock alter
######################################

from oscar.apps.dashboard.catalogue.views import StockAlertListView
from .forms import CustomStockAlertSearchForm


class CustomStockAlertListView(StockAlertListView):
    """
    Oscar extended method for stockalert.
    """

    template_name = 'dashboard/catalogue/stockalert_list.html'
    model = StockAlert
    context_object_name = 'alerts'
    paginate_by = settings.OSCAR_STOCK_ALERTS_PER_PAGE

    partner_stock = StockRecord
    partner_model = Partner

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form
        ctx['description'] = self.description
        return ctx

    def get_queryset(self):

        self.description = _('All alerts')

        stock_record = StockRecord.objects.filter(product__is_deleted=False)
        queryset = self.model.objects.filter(stockrecord__in=stock_record)

        if not self.request.user.is_superuser:
            partner_id = self.partner_model.objects.get(users=self.request.user)
            partner_stock = self.partner_stock.objects.filter(partner=partner_id.id).values_list('id', flat=True)
            queryset = queryset.filter(stockrecord__in=partner_stock)

        data = self.request.GET

        if data.get('product'):
            product = data.get('product')
            stock_record = StockRecord.objects.filter(product=product)
            queryset = queryset.filter(stockrecord__in=stock_record)

        if data.get('status'):
            status = data.get('status')
            # stock_record = StockRecord.objects.filter(product=product)
            queryset = queryset.filter(status=status)

        self.form = CustomStockAlertSearchForm()

        return queryset


def export_combo(request):
    """

    :param request:
    :return:
    """

    try:

        data = request.GET
        product_class = ProductClass.objects.get(name='Combo')
        queryset = Product.objects.filter(product_class=product_class, is_deleted=False)

        if request.user.is_superuser:
            queryset = Product.objects.filter(product_class=product_class, is_deleted=False)

        if request.user.is_staff and not request.user.is_superuser:
            user = User.objects.get(id=request.user.id)
            partner = Partner.objects.filter(users=user).last()
            partner_stocks = StockRecord.objects.filter(partner=partner).values_list('product__id', flat=True)
            queryset = Product.objects.filter(product_class=product_class, id__in=partner_stocks, is_deleted=False)

        if data.get('product_title'):
            product_title = data.get('product_title')
            queryset = queryset.filter(title__icontains=product_title)

        if data.get('upc'):
            upc = data.get('upc')
            queryset = queryset.filter(upc=upc)

        if data.get('status'):
            queryset = queryset.filter(is_approved=data.get('status'))

        if data.get('vendor_name'):
            partner = Partner.objects.filter(name__icontains=data.get('vendor_name'))
            stock_record = StockRecord.objects.filter(partner__id__in=partner.values_list('id', flat=True))
            queryset = queryset.filter(id__in=stock_record.values_list('product', flat=True))

        excel_data = [
            [
                'Sr. No', 'Product Title', 'UPC', 'Offer Cost',
                'Valid From date', 'Valid To date', 'Status',
            ]
        ]

        counter = 0

        for obj in queryset:
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(obj.title),
                    str(obj.upc),
                    str(obj.combo_price),
                    str(obj.combo_start_date.date()),
                    str(obj.combo_end_date.date()),
                    str(obj.is_approved),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'combo_product_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_events(request):
    """
    Method to export event
    :param request: default
    :return: xlsx:
    """

    try:

        data = request.GET

        user = request.user
        if user.is_superuser:
            queryset = _VendorCalender.objects.filter(product__is_deleted=False)
        else:
            partner = Partner.objects.get(users=user)
            queryset = _VendorCalender.objects.filter(vendor=partner, product__is_deleted=False)

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('product'):
            product = data.get('product')
            queryset = queryset.filter(product=product)

        if data.get('category') and data.get('sub_category'):
            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))
            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            queryset = queryset.filter(product__categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            queryset = queryset.filter(product__categories__in=id_list)
            # queryset = queryset.filter(product__categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            queryset = queryset.filter(product__categories__in=category.values_list('id', flat=True))

        excel_data = [
            [
                'Sr. No', 'Product', 'From date', 'To date'
            ]
        ]

        counter = 0

        for calendar in queryset:
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(calendar.product), str(calendar.from_date.date()),
                    str(calendar.to_date.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'event_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_bookedevents(request):
    """
    Method to export event
    :param request: default
    :return: xlsx:
    """

    try:

        data = request.GET

        # user = request.user
        # partner = Partner.objects.get(users=user)
        queryset = _VendorCalender.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('product'):
            product = data.get('product')
            queryset = queryset.filter(product=product)

        excel_data = [
            [
                'Sr. No', 'Product', 'ASP', 'From date', 'To date'
            ]
        ]

        counter = 0

        for calendar in queryset:
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(calendar.product), str(calendar.vendor), str(calendar.from_date.date()),
                    str(calendar.to_date.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'bookedevent_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_coupon(request):
    """
    Method to export coupon
    :param request: default
    :return: xlsx
    """

    try:

        data = request.GET
        c_obj = CustomizeCouponModel.objects.distinct('voucher').values('voucher__id')
        queryset = Voucher.objects.exclude(id__in=c_obj).order_by('-date_created')

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('name'):
            queryset = queryset.filter(name__icontains=data.get('name'))

        if data.get('code'):
            queryset = queryset.filter(code__icontains=data.get('code'))

        excel_data = [
            [
                'Sr. No', 'Name', 'Code', 'Status', 'Categories', 'Applied on carts', 'Num of orders', 'Date created'
            ]
        ]

        counter = 0
        is_active = '-'

        for voucher in queryset:

            counter = counter + 1

            if voucher.is_active:
                is_active = 'Active'
            else:
                is_active = 'Inactive'

            cat_names = ''
            if voucher.benefit.range.included_categories.all().count() > 0:
                cat_names = voucher.benefit.range.get_cat

            excel_data.append(
                [
                    str(counter), str(voucher.name), str(voucher.code), is_active, str(cat_names),
                    str(voucher.num_basket_additions), str(voucher.num_orders),
                    str(voucher.date_created.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'coupon_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_season(request):
    """
    Method to export coupon season
    :param request: default
    :return: xlsx
    """

    try:

        data = request.GET
        queryset = Range.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('season_name'):
            season_name = data.get('season_name')
            queryset = queryset.filter(name__icontains=season_name)

        excel_data = [
            [
                'Sr. No', 'Name', 'Num product', 'Date created'
            ]
        ]

        counter = 0
        num_product = 'All'

        for data in queryset:
            counter = counter + 1

            if data.includes_all_products:
                num_product = 'All'
            else:
                num_product = data.num_products()

            excel_data.append(
                [
                    str(counter), str(data.name), str(num_product), str(data.date_created.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'coupon_season_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_low_stock(request):
    """
    Method to export low stock reviews.
    :param request: default
    :return: xlsx
    """

    try:

        data = request.GET
        queryset = StockAlert.objects.all()

        if not request.user.is_superuser:
            partner_id = Partner.objects.get(users=request.user)
            partner_stock = Partner.objects.filter(partner=partner_id.id).values_list('id', flat=True)
            queryset = queryset.filter(stockrecord__in=partner_stock)

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('product'):
            product = data.get('product')
            stock_record = StockRecord.objects.filter(product=product)
            queryset = queryset.filter(stockrecord__in=stock_record)

        if data.get('status'):
            status = data.get('status')
            # stock_record = StockRecord.objects.filter(product=product)
            queryset = queryset.filter(status=status)

        excel_data = [
            [
                'Sr. No', 'Product', 'ASP', 'Low stock threshold', 'Current available stock', 'Date alert raised',
                'Status'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1
            excel_data.append(
                [
                    str(counter), str(data.stockrecord.product.get_title()), str(data.stockrecord.partner.display_name),
                    str(data.stockrecord.low_stock_threshold), str(data.stockrecord.net_stock_level),
                    str(data.date_created.date()),
                    str(data.status)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'lowstock_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_reviews(request):
    """
    Method to export customer reviews.
    :param request: default
    :return: xlsx
    """

    try:

        data = request.GET

        queryset = ProductReview.objects.filter(product__is_deleted=False)

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('title'):
            title = data.get('title')
            queryset = queryset.filter(title__icontains=title)

        if data.get('rating'):
            rating = data.get('rating')
            queryset = queryset.filter(score=rating)

        if data.get('status'):
            queryset = queryset.filter(status=data.get('status'))

        if data.get('date'):
            date = data.get('date')
            queryset = queryset.filter(date_created__date=date)

        if data.get('month'):
            month = data.get('month')
            queryset = queryset.filter(date_created__month=month)

        if data.get('year'):
            year = data.get('year')
            queryset = queryset.filter(date_created__year=year)

        if data.get('category'):
            category = data.get('category')
            product = Product.objects.filter(categories=category, is_deleted=False)
            queryset = queryset.filter(product__in=product)

        excel_data = [
            [
                'Sr. No', 'Title',
                # 'Product',
                'Category',
                'User', 'Score', 'Status', 'Date created'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1
            excel_data.append(
                [
                    str(counter), str(data.title),
                    # str(data.product.title),
                    str(data.product.categories.all().last()),
                    str(data.reviewer_name),
                    str(data.score), str(data.get_status_display()), str(data.date_created)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'reviews_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_users(request):
    """
    Method to export customer intp xls.
    :param request:
    :return:
    """

    try:

        queryset = User.objects.all()

        data = request.GET

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('email'):
            email = normalise_email(data.get('email'))
            queryset = queryset.filter(email__icontains=email)

        if data.get('name'):
            parts = data.get('name').split()
            condition = Q()
            for part in parts:
                condition &= Q(first_name__icontains=part) | Q(last_name__icontains=part)

            queryset = queryset.filter(condition)

        if data.get('status'):
            queryset = queryset.filter(is_active=data.get('status'))

        excel_data = [
            [
                'Sr. No', 'Name', 'Email ID', 'Is active'
            ]
        ]

        counter = 0
        name = '-'

        for data in queryset:

            if data.first_name:
                name = data.first_name + " " + data.last_name
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(name), str(data.email), str(data.is_active)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'customers_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:

        import os
        import sys
        print('-----------in exception----------')
        print(e.args)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_orders(request):
    """
    Method to export order into xls.
    :param request:
    :return:
    """

    try:

        data = request.GET
        queryset = Order.objects.all()

        if not request.user.is_superuser and request.user.is_staff:
            partners = Partner.objects.filter(users=request.user)
            # queryset = queryset.filter(lines__partner__in=partners).distinct()
            allocated_orders = OrderAllocatedVendor.objects.filter(vendor=partners.last())
            queryset = queryset.filter(
                lines__id__in=allocated_orders.values_list('order_line__id', flat=True)).distinct()

        if data.get('checked_id'):
            order_id = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=order_id)

        if data.get('order_number'):
            queryset = queryset.filter(number__icontains=data.get('order_number'))

        if data.get('name'):
            # If the value is two words, then assume they are first name and
            # last name
            parts = data.get('name').split()
            allow_anon = getattr(settings, 'OSCAR_ALLOW_ANON_CHECKOUT', False)

            if len(parts) == 1:
                parts = [data.get('name'), data.get('name')]
            else:
                parts = [parts[0], parts[1:]]

            filter = Q(user__first_name__istartswith=parts[0])
            filter |= Q(user__last_name__istartswith=parts[1])
            if allow_anon:
                filter |= Q(billing_address__first_name__istartswith=parts[0])
                filter |= Q(shipping_address__first_name__istartswith=parts[0])
                filter |= Q(billing_address__last_name__istartswith=parts[1])
                filter |= Q(shipping_address__last_name__istartswith=parts[1])

            queryset = queryset.filter(filter).distinct()

        if data.get('status'):
            status = data.get('status')
            queryset = queryset.filter(status__icontains=status)

        if data.get('product'):
            product = data.get('product')
            order_line = OrderLine.objects.filter(product=product)
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('category') and data.get('sub_category'):
            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            order_line = OrderLine.objects.filter(product__categories__in=category_list)
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            order_line = OrderLine.objects.filter(product__categories__in=id_list)

            # order_line = OrderLine.objects.filter(product__categories__in=category.values_list('id', flat=True))
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            order_line = OrderLine.objects.filter(product__categories__in=category.values_list('id', flat=True))
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        excel_data = [
            [
                'Sr. No', 'Order Number', 'Customer Name', 'Order value', 'Date placed',
                'Address', 'Order status'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1
            name = " "
            if data.user:
                if data.user.first_name and data.user.last_name:
                    name = data.user.first_name + " " + data.user.last_name
                elif data.user.first_name and not data.user.last_name:
                    name = data.user.first_name
                elif not data.user.first_name and data.user.last_name:
                    name = data.user.last_name

            excel_data.append(
                [
                    str(counter), str(data.number),
                    str(name),
                    str(data.total_incl_tax),
                    str(data.date_placed.date()), str(data.shipping_address),
                    str(data.status)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'order_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_units(request):
    """
    Method to export units.
    """

    try:

        queryset = ProductUnit.objects.all()

        data = request.GET

        if data.get('checked_id'):
            unit_id = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=unit_id)

        if data.get('unit'):
            queryset = queryset.filter(unit__icontains=data.get('unit'))

        excel_data = [
            [
                'Sr. No', 'Unit'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(data.unit)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'unit_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_products(request):
    """
    Method to download product in excel.
    :param request: form data
    :return: xls file.
    """

    try:

        queryset = Product.objects.all()

        if ProductClass.objects.filter(name='Combo'):
            combo_class = ProductClass.objects.filter(name='Combo').last()
            queryset = queryset.exclude(product_class=combo_class)

        if request.user.is_staff and not request.user.is_superuser:
            auth_user = request.user
            partner_obj = Partner.objects.get(users=auth_user)
            queryset = queryset.filter(stockrecords__partner=partner_obj)

        data = request.GET

        if data.get('checked_id'):
            product_id = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=product_id)

        if data.get('status'):
            queryset = queryset.filter(is_approved=data.get('status'))

        if data.get('category') and data.get('sub_category'):
            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            queryset = queryset.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            queryset = queryset.filter(categories__in=id_list)
            # queryset = queryset.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            queryset = queryset.filter(categories__in=category.values_list('id', flat=True))

        if data.get('is_image'):

            product_with_image = ProductImage.objects.filter(product__id__in=queryset.values_list('id', flat=True))

            if data.get('is_image') == '1':  # Has image
                queryset = queryset.filter(id__in=product_with_image.values_list('product', flat=True))
            else:
                queryset = queryset.exclude(id__in=product_with_image.values_list('product', flat=True))

        if data.get('product_type'):

            product_class = None

            if data.get('product_type') == '1':  # Sale
                product_class = ProductClass.objects.filter(name='Sale')

            if data.get('product_type') == '2':  # Rent
                product_class = ProductClass.objects.filter(name='Rent')

            if data.get('product_type') == '3':  # Rent Or Sale
                product_class = ProductClass.objects.filter(name='Rent Or Sale')

            if data.get('product_type') == '4':  # Service
                product_class = ProductClass.objects.filter(name='Service')

            if data.get('product_type') == '5':  # Professional
                product_class = ProductClass.objects.filter(name='Professional')

            if product_class:
                queryset = queryset.filter(product_class=product_class.last())

        if data.get('upc'):

            matches_upc = Product.objects.filter(upc=data['upc'], is_deleted=False)
            qs_match = queryset.filter(Q(id__in=matches_upc.values('id')) | Q(id__in=matches_upc.values('parent_id')))

            if qs_match.exists():
                queryset = qs_match
            else:
                matches_upc = Product.objects.filter(upc__icontains=data['upc'], is_deleted=False)
                queryset = queryset.filter(
                    Q(id__in=matches_upc.values('id')) | Q(id__in=matches_upc.values('parent_id')))

        if data.get('title'):
            queryset = queryset.filter(title__icontains=data['title'])

        if data.get('vendor_pincode'):
            partner = Partner.objects.filter(pincode__icontains=data.get('vendor_pincode'))
            stock_record = StockRecord.objects.filter(partner__id__in=partner.values_list('id', flat=True))
            queryset = queryset.filter(id__in=stock_record.values_list('product', flat=True))

        if data.get('vendor_name'):
            partner = Partner.objects.filter(name__icontains=data.get('vendor_name'))
            stock_record = StockRecord.objects.filter(partner__id__in=partner.values_list('id', flat=True))
            queryset = queryset.filter(id__in=stock_record.values_list('product', flat=True))

        excel_data = [
            [
                'Sr. No', 'Product Name', 'Product UPC', 'Category', 'Product Class',
                'Product Status', 'ASP Name', 'ASP Status', 'ASP Pincode',
                'Is Combo Product'
            ]
        ]

        counter = 0
        vendor_name = '-'
        vendor_status = '-'
        vendor_pincode = '-'
        is_combo = 'No'

        for data in queryset:
            counter = counter + 1

            if data.is_combo_product:
                is_combo = 'Yes'
            else:
                is_combo = 'No'

            if data.table_vendor_name:
                vendor_name = data.table_vendor_name.name
                vendor_pincode = data.table_vendor_name.pincode
                vendor_status = data.table_vendor_name.users.last().is_active
                if vendor_status:
                    vendor_status = 'Active'
                else:
                    vendor_status = 'InActive'
            if data.is_deleted:
                approved_status = 'Deleted'
            else:
                approved_status = str(data.is_approved)
            excel_data.append(
                [
                    str(counter), str(data.title), str(data.upc),
                    str(data.categories.last()), str(data.product_class),
                    # str(data.is_approved),
                    approved_status,
                    str(vendor_name), str(vendor_status),
                    str(vendor_pincode), is_combo
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'products_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_categories(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categories.csv"'

    queryset = Category.objects.all()

    writer = csv.writer(response)
    writer.writerow(['Name', 'Description'])

    for category in queryset:
        regex_for_tag = re.compile('<.*?>')
        description = re.sub(regex_for_tag, '', category.description)
        writer.writerow([
            category.name,
            description
        ])
    return response


def export_category(request):
    """
    Method to download categories into xls.
    :param request: data
    :return: xls
    """

    if not request.user.is_superuser:
        messages.error(request, 'Invalid request.')
        return redirect('/dashboard')

    try:

        data = request.GET
        queryset = Category.objects.all()

        if data.get('checked_id'):
            category_id = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=category_id)

        excel_data = [
            [
                'Sr. No', 'Name', 'Description'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1
            regex_for_tag = re.compile('<.*?>')
            description = re.sub(regex_for_tag, '', data.description)
            excel_data.append(
                [
                    str(counter), str(data.name), description
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'category_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_vendors(request):
    """
    Method to download partner report in excel.
    """

    try:

        qs = Partner.objects.all()
        data = request.GET

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            qs = qs.filter(id__in=checked_list)

        if data['status']:
            js = Partner.objects.all().values_list('users')
            xs = User.objects.filter(id__in=js, is_active=data['status']).values_list('id')
            qs = qs.filter(users__in=xs)

        if data.get('pincode'):
            qs = qs.filter(pincode__icontains=data.get('pincode'))

        if data.get('search_type') and data.get('all_search'):

            search_text = data.get('all_search')
            search_type = data.get('search_type')

            if search_type == '1':  # by vendor name
                qs = qs.filter(name__icontains=search_text)

            if search_type == '2':  # by vendor email
                qs = qs.filter(email_id__icontains=search_text)

            if search_type == '3':  # by business name
                qs = qs.filter(business_name__icontains=search_text)

            if search_type == '4':  # by pin code
                qs = qs.filter(pincode__icontains=search_text)

            if search_type == '5':  # by phone number
                qs = qs.filter(
                    Q(telephone_number__icontains=search_text) | Q(alternate_mobile_number__icontains=search_text)
                )

        excel_data = [
            [
                'Sr. No', 'ASP Name', 'ASP Email', 'Business Name', 'Addresses',
                'Pincode', 'Phone Number', 'Alt. Phone Number', 'Status'
            ]
        ]

        counter = 0
        vendor_name = '-'
        vendor_email = '-'
        vendor_business = '-'
        vendor_address = '-'
        vendor_pincode = '-'
        vendor_number = '-'
        vendor_al_number = '-'
        vendor_status = '-'

        for data in qs:

            counter = counter + 1

            if data.name:
                vendor_name = str(data.name)
            if data.email_id:
                vendor_email = str(data.email_id)
            if data.business_name:
                vendor_business = str(data.business_name)
            if data.vendor_full_address:
                vendor_address = str(data.vendor_full_address)
            if data.pincode:
                vendor_pincode = str(data.pincode)
            if data.telephone_number:
                vendor_number = str(data.telephone_number)
            if data.alternate_mobile_number:
                vendor_al_number = str(data.alternate_mobile_number)
            if data.alternate_mobile_number:
                vendor_al_number = str(data.alternate_mobile_number)
            if data.vendor_status:
                vendor_status = str(data.vendor_status)

            excel_data.append(
                [
                    str(counter), vendor_name, vendor_email,
                    vendor_business, vendor_address, vendor_pincode,
                    vendor_number, vendor_al_number, vendor_status
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'vendor_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:

        print(e.args)

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_customers(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    # queryset = User.objects.filter(is_staff=False)
    queryset = User.objects.all()
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email ID', 'Mobile Number', 'Is Active'])
    for user in queryset:
        name = user.first_name + " " + user.last_name
        try:
            custom_profile = CustomProfile.objects.get(user=user)
            mobile_number = custom_profile.mobile_number
        except:
            mobile_number = ""
        writer.writerow([
            name,
            user.email,
            mobile_number,
            user.is_active
        ])

    return response


# from datetime import *

def add_admin_notes(request):
    try:
        note = request.POST['reason_event']
        date_created = datetime.datetime.now()
        event_start_date = request.POST['event_start_date']
        x = event_start_date.split("-")
        event_start_date = datetime.datetime(year=int(x[0]), month=int(x[1]), day=int(x[2]))
        timepicker1 = request.POST.get('timepicker1')
        date = date_created.strptime(timepicker1, '%I:%M %p')

        dt = date.replace(year=event_start_date.year, month=event_start_date.month, day=event_start_date.day)
        user = User.objects.get(username=request.user.username)

        notes = Notes.objects.create(
            created_by=user,
            note=note,
            start_date=dt,
        )
        notes.save()

        messages.success(request, _("Note saved successfully"))
    except Exception as e:
        print(e.args)
        messages.error(request, "Something went wrong")
    return redirect('/dashboard/partners/calender')


def deactivate_note(request, id):
    try:
        notes = Notes.objects.get(id=id)
        notes.is_active = False
        notes.save()

        messages.success(request, _("Note deactivated successfully"))
    except Exception as e:
        print(e.args)
        messages.error(request, "Something went wrong")
    return redirect('/dashboard')


class SalesListView(generic.ListView):
    """
    Method to view vendor calendar.
    """

    template_name = 'dashboard/sales/index.html'
    context_object_name = 'calendars'
    model = _VendorCalender
    queryset = _VendorCalender.objects.all()
    form_class = dash_form.VendorCalenderSearchForm1

    def get_queryset(self):

        """
        Return vendor wise queryset
        :return: queryset
        """

        data = self.request.GET
        user = self.request.user
        queryset = self.model.objects.all()

        if data.get('product'):
            product = data.get('product')
            queryset = queryset.filter(product=product)
        if data.get('upc'):
            upc = data.get('upc')
            queryset = queryset.filter(product__upc=upc)
        if data.get('vendor'):
            vendor = data.get('vendor')
            queryset = queryset.filter(vendor=vendor)
        if data.get('date'):
            date = data.get('date')
            queryset = queryset.filter(from_date__date=date)

        return queryset

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx


class CustomPartnerDeleteView(PartnerDeleteView):
    model = Partner
    template_name = 'dashboard/partners/partner_delete.html'

    def get_success_url(self):
        messages.success(self.request,
                         _("Partner '%s' was deleted successfully.") %
                         self.object.name)
        return reverse('dashboard:partner-list')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        qs = Product.objects.all()
        qs_obj = qs.filter(stockrecords__partner=self.object).update(is_deleted=True)

        User.objects.filter(id=self.object.users.last().id).delete()

        self.object.delete()
        return HttpResponseRedirect(success_url)


class CustomRangeCreateView1(RangeCreateView):
    """
    Oscar extended range create view.
    """

    template_name = 'dashboard/ranges/range_form.html'
    form_class = CustomRangeForm

    def get_success_url(self):
        if 'action' in self.request.POST:
            return reverse('dashboard:range-products',
                           kwargs={'pk': self.object.id})
        else:
            msg = render_to_string(
                'dashboard/ranges/messages/range_saved.html',
                {'range': self.object})
            messages.success(self.request, msg, extra_tags='safe noicon')
            return reverse('dashboard:voucher-create', args=(self.object.id,))

    def _get_form(request, formcls, prefix):
        data = request.POST if prefix in request.POST else None
        return formcls(data, prefix=prefix)


class CustomVoucherListView1(VoucherListView):
    """
    Oscar extended voucher list view
    """

    form_class = VoucherSearchForm
    template_name = 'dashboard/vouchers/new/voucher_list.html'

    def get_queryset(self):

        """
        method to return queryset.
        :return: queryset
        """
        c_obj = CustomizeCouponModel.objects.distinct('voucher').values('voucher__id')
        qs = self.model.objects.exclude(id__in=c_obj).order_by('-date_created')
        qs = sort_queryset(
            qs, self.request,
            ['num_basket_additions', 'num_orders', 'date_created'], '-date_created'
        )

        self.description_ctx = {
            'main_filter': _('All vouchers'),
            'name_filter': '',
            'code_filter': ''
        }

        # If form not submitted, return early
        is_form_submitted = 'name' in self.request.GET
        if not is_form_submitted:
            self.form = self.form_class()
            return qs.filter(voucher_set__isnull=True)

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data
        if data['name']:
            qs = qs.filter(name__icontains=data['name'])

        if data['code']:
            qs = qs.filter(code__icontains=data['code'])

        if not data['in_set']:
            qs = qs.filter(voucher_set__isnull=True)

        return qs


class CustomRangeCreateView1(RangeCreateView):
    """
    Oscar extended range create view.
    """

    template_name = 'dashboard/ranges/range_form.html'
    form_class = CustomRangeForm

    def get_success_url(self):
        if 'action' in self.request.POST:
            return reverse('dashboard:range-products',
                           kwargs={'pk': self.object.id})
        else:
            msg = render_to_string(
                'dashboard/ranges/messages/range_saved.html',
                {'range': self.object})
            messages.success(self.request, msg, extra_tags='safe noicon')
            return reverse('dashboard:voucher-create', args=(self.object.id,))


def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)


ConditionalOffer = get_model('offer', 'ConditionalOffer')
Condition = get_model('offer', 'Condition')

from django.db import transaction

Benefit = get_model('offer', 'Benefit')


class CustomVoucherCreateView1(VoucherCreateView):
    """
    Oscar extended voucher create view
    """

    template_name = 'dashboard/vouchers/new/voucher_form.html'
    form_class = VoucherForm1
    custom_range_form = CustomRangeForm1

    def get_context_data(self, **kwargs):
        ctx = super(CustomVoucherCreateView1, self).get_context_data(**kwargs)
        ctx['title'] = _('Create voucher')
        ctx['form1'] = self.custom_range_form(prefix='custom')
        return ctx

    @transaction.atomic()
    def form_valid(self, form):
        # Create offer and benefit
        custom_form = self.custom_range_form(self.request.POST)
        custom_form.name = form.cleaned_data['name']

        if custom_form.is_valid():
            a = custom_form.save(commit=False)
            a.is_public = True
            a.includes_all_products = True
            vend = self.request.POST.getlist('custom-included_categories')
            des = self.request.POST['custom-description']
            billing_amount = self.request.POST['custom-min_billing_amount']
            if billing_amount == '':
                billing_amount = 0
            a.save()
            a.included_categories.add(*vend)
            a.description = des
            a.min_billing_amount = billing_amount
            a.save()
            form.benefit_range = a

            condition = Condition.objects.create(
                range=a,
                type=Condition.COUNT,
                value=1
            )
            benefit = Benefit.objects.create(
                range=a,
                type=form.cleaned_data['benefit_type'],
                value=form.cleaned_data['benefit_value']
            )
            name = form.cleaned_data['name']
            offer = ConditionalOffer.objects.create(
                name=_("Offer for voucher '%s'") % name,
                offer_type=ConditionalOffer.VOUCHER,
                benefit=benefit,
                condition=condition,
                exclusive=form.cleaned_data['exclusive'],
            )
            voucher = Voucher.objects.create(
                name=name,
                code=form.cleaned_data['code'],
                usage=form.cleaned_data['usage'],
                start_datetime=form.cleaned_data['start_datetime'],
                end_datetime=form.cleaned_data['end_datetime'],
            )
            voucher.offers.add(offer)
            return HttpResponseRedirect(self.get_success_url())
        return self.form_invalid(custom_form)

    def get_success_url(self):
        messages.success(self.request, _("Voucher created"))
        return reverse('dashboard:voucher-list1')


class CustomVoucherUpdateView1(VoucherUpdateView):
    """
    Oscar extended voucher update view
    """
    template_name = 'dashboard/vouchers/new/voucher_form.html'
    form_class = VoucherForm1
    custom_range_form = CustomRangeForm1

    def get_context_data(self, **kwargs):
        ctx = super(CustomVoucherUpdateView1, self).get_context_data(**kwargs)
        ctx['title'] = self.voucher.name
        ctx['voucher'] = self.voucher
        voucher = self.get_voucher()
        offer = voucher.offers.all()[0]
        benefit = offer.benefit
        ctx['form1'] = self.custom_range_form(prefix='custom', initial={'description': benefit.range.description,
                                                                        'included_categories': benefit.range.included_categories.all(),
                                                                        'min_billing_amount': benefit.range.min_billing_amount})
        return ctx

    def get_initial(self):
        voucher = self.get_voucher()
        offer = voucher.offers.all()[0]
        benefit = offer.benefit
        return {
            'name': voucher.name,
            'code': voucher.code,
            'start_datetime': voucher.start_datetime,
            'end_datetime': voucher.end_datetime,
            'usage': voucher.usage,
            'benefit_type': benefit.type,
            'benefit_range': benefit.range,
            'benefit_value': benefit.value,
            'exclusive': offer.exclusive,
        }

    @transaction.atomic()
    def form_valid(self, form):
        custom_form = self.custom_range_form(self.request.POST)

        vend = self.request.POST.getlist('custom-included_categories')
        des = self.request.POST['custom-description']
        billing_amount = self.request.POST['custom-min_billing_amount']

        voucher = self.get_voucher()
        voucher.name = form.cleaned_data['name']
        voucher.code = form.cleaned_data['code']
        voucher.usage = form.cleaned_data['usage']
        voucher.start_datetime = form.cleaned_data['start_datetime']
        voucher.end_datetime = form.cleaned_data['end_datetime']
        voucher.save()

        offer = voucher.offers.all()[0]
        offer.condition.range = form.cleaned_data['benefit_range']
        offer.condition.save()

        offer.exclusive = form.cleaned_data['exclusive']
        offer.save()

        benefit = voucher.benefit
        # benefit.range = a
        benefit.range.description = des
        benefit.range.included_categories.set(vend)
        benefit.range.name = voucher.name
        benefit.range.min_billing_amount = self.request.POST['custom-min_billing_amount']
        benefit.range.save()
        benefit.type = form.cleaned_data['benefit_type']
        benefit.value = form.cleaned_data['benefit_value']
        benefit.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, _("Voucher created"))
        return reverse('dashboard:voucher-list1')


class CustomVoucherUpdateView1(VoucherUpdateView):
    """
    Oscar extended voucher update view
    """
    template_name = 'dashboard/vouchers/new/voucher_form.html'
    form_class = VoucherForm1
    custom_range_form = CustomRangeForm1

    def get_context_data(self, **kwargs):
        ctx = super(CustomVoucherUpdateView1, self).get_context_data(**kwargs)
        ctx['title'] = self.voucher.name
        ctx['voucher'] = self.voucher
        voucher = self.get_voucher()
        offer = voucher.offers.all()[0]
        benefit = offer.benefit
        ctx['form1'] = self.custom_range_form(prefix='custom', initial={'description': benefit.range.description,
                                                                        'included_categories': benefit.range.included_categories.all(),
                                                                        'min_billing_amount': benefit.range.min_billing_amount})
        return ctx

    def get_initial(self):
        voucher = self.get_voucher()
        offer = voucher.offers.all()[0]
        benefit = offer.benefit
        return {
            'name': voucher.name,
            'code': voucher.code,
            'start_datetime': voucher.start_datetime,
            'end_datetime': voucher.end_datetime,
            'usage': voucher.usage,
            'benefit_type': benefit.type,
            'benefit_range': benefit.range,
            'benefit_value': benefit.value,
            'exclusive': offer.exclusive,
        }

    @transaction.atomic()
    def form_valid(self, form):
        custom_form = self.custom_range_form(self.request.POST)

        vend = self.request.POST.getlist('custom-included_categories')
        des = self.request.POST['custom-description']
        billing_amount = self.request.POST['custom-min_billing_amount']

        voucher = self.get_voucher()
        voucher.name = form.cleaned_data['name']
        voucher.code = form.cleaned_data['code']
        voucher.usage = form.cleaned_data['usage']
        voucher.start_datetime = form.cleaned_data['start_datetime']
        voucher.end_datetime = form.cleaned_data['end_datetime']
        voucher.save()

        offer = voucher.offers.all()[0]
        offer.condition.range = form.cleaned_data['benefit_range']
        offer.condition.save()

        offer.exclusive = form.cleaned_data['exclusive']
        offer.save()

        benefit = voucher.benefit
        # benefit.range = a
        benefit.range.description = des
        benefit.range.included_categories.set(vend)
        benefit.range.name = voucher.name
        if self.request.POST['custom-min_billing_amount']:
            benefit.range.min_billing_amount = self.request.POST['custom-min_billing_amount']
        benefit.range.save()
        benefit.type = form.cleaned_data['benefit_type']
        benefit.value = form.cleaned_data['benefit_value']
        benefit.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, _("Voucher created"))
        return reverse('dashboard:voucher-list1')


class CustomVoucherStatsView(VoucherStatsView):
    template_name = 'dashboard/vouchers/new/voucher_detail.html'

