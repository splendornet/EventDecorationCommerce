# python imports
import datetime, json

# django imports
from django.shortcuts import HttpResponse, render, redirect
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
from django.db.models import Q

# packages imports
from oscar.core.loading import get_class, get_model

# internal import
from .customized_order_forms import *
from .customized_order_formset import *

Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
Enquiry = get_model('customer', 'Enquiry')

Basket = get_model('basket', 'Basket')
BasketLine = get_model('basket', 'Line')

Partner = get_model('partner', 'Partner')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')
Attribute = get_model('catalogue', 'Attribute')
StockRecord = get_model('partner', 'StockRecord')

generate_excel = get_class('dashboard.utils', 'generate_excel')
get_product_price = get_class('basket.bind', 'get_product_price')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')


class CustomOrdersListView(generic.ListView):

    model = Order
    template_name = 'dashboard/sales/custom_order/list.html'
    context_object_name = 'orders'
    paginate_by = 10
    form_class = CustomOrderSearchForm
    select_user_form = CustomOrderSelectCustomerForm

    def get(self, request, *args, **kwargs):

        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        data = self.request.GET

        qs = self.model.objects.filter(customized_order=True)

        if data.get('order_number'):
            qs = qs.filter(number__icontains=data.get('order_number'))

        if data.get('product'):
            product = data.get('product')
            order_line = OrderLine.objects.filter(product=product)
            qs = qs.filter(id__in=order_line.values_list('order', flat=True))

        return qs

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class
        ctx['select_user_form'] = self.select_user_form

        return ctx


class CreateCustomOrder(generic.View):

    template_name = 'dashboard/sales/custom_order/form.html'
    form_class = CustomOrderSelectCustomerForm
    formset = BasketSet

    def is_invalid(self, message):

        messages.error(self.request, message)
        return redirect('dashboard:index')

    def get(self, request, *args, **kwargs):

        context = dict()
        customer_id = request.GET.get('customer')
        enquiry_id = request.GET.get('enq')

        if not customer_id or not User.objects.filter(id=customer_id, is_staff=False, is_active=True):
            return self.is_invalid('Invalid customer.')

        customer = User.objects.get(id=customer_id)

        # delete old open custom baskets
        Basket.objects.filter(owner=customer, status='Open', customized_basket=True).delete()

        # create new basket
        cart_data = {
            'customized_basket': True,
            'owner':customer
        }

        basket = Basket.objects.create(**cart_data)

        context['form'] = self.form_class
        context['customer'] = customer
        context['basket'] = basket
        context['formsets'] = self.formset
        context['enquiry_id'] = enquiry_id

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            basket = Basket.objects.get(id=request.POST.get('basket_temp'))
            enquiry = Enquiry.objects.get(id=request.POST.get('enquiry_id'))

            cart_data = request.POST.get('cart_json')
            cart_data_json = json.loads(cart_data)

            for form in cart_data_json:

                product_price, product_rent_price = 0, 0
                start_date, end_date = datetime.datetime.now(), datetime.datetime.now()
                product_id = form.get('product')

                product = Product.objects.get(id=product_id)

                stockrecord = StockRecord.objects.get(product=product)
                stock_info = StockRecord.objects.get(product=product)

                line_reference = str(product.id) + '_' + str(stockrecord.id)

                order_type = form.get('order_type')
                quantity = form.get('qty')
                booking_start_date = form.get('booking_start_date')
                booking_end_date = form.get('booking_end_date')

                if order_type == 'Sale':
                    # set current date by default
                    start_date, end_date = datetime.datetime.now(), datetime.datetime.now()
                    product_price = get_product_price(stock_info, 'Sale', quantity)
                    product_rent_price = stock_info.rent_price

                if order_type in ['Rent', 'Professional']:
                    product_price = get_product_price(stock_info, 'Rent', quantity)
                    product_rent_price = product_price

                if order_type == 'Rent':
                    start_date = booking_start_date
                    end_date = booking_end_date

                if order_type == 'Professional':
                    start_date = datetime.datetime.strptime(booking_start_date, '%Y-%m-%d %I:%M %p')
                    end_date = datetime.datetime.strptime(booking_end_date, '%Y-%m-%d %I:%M %p')

                BasketLine.objects.create(
                    basket=basket, line_reference=line_reference,
                    product=product, stockrecord=stockrecord,
                    quantity=form.get('qty'),
                    price_excl_tax=product_price,
                    price_currency=stock_info.price_currency,
                    advance_payment_percentage=stock_info.advance_payment_percentage,
                    minimum_qty=stock_info.minimum_qty, tax_percentage=stock_info.tax_percentage,
                    shipping_charges=stock_info.shipping_charges, rent_price=product_rent_price,
                    order_type=order_type, booking_start_date=start_date, booking_end_date=end_date
                )

            basket.status = 'Frozen'
            basket.save()

            enquiry.basket_instance = basket
            enquiry.save()

            messages.success(request, 'Order created successfully.')
            return redirect('/dashboard/partners/best_quote')

        except:

            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard')


def get_product_attribute(request):

    data = request.GET

    product_id = data.get('product_id')
    row = data.get('row')
    product = Product.objects.get(id=product_id)

    if data.get('call_type') == '1':
        return HttpResponse(product.product_class.name)

    master_attrs = Attribute.objects.all()
    attrs = Attribute_Mapping.objects.filter(product=product)

    attrs_list = []

    from django.template.loader import render_to_string

    context = dict()

    for attr in master_attrs:

        attrs_dict = dict()

        if attrs.filter(attribute=attr).values_list('value', flat=True):
            attrs_dict['name'] = attr.attribute
            attrs_dict['values'] = list(attrs.filter(attribute=attr).values_list('value', flat=True))
            attrs_list.append(attrs_dict)

    context['row'] = row
    context['attrs_list'] = attrs_list
    context['product'] = product

    m = render_to_string('dashboard/sales/custom_order/product_data.html', context=context)

    return HttpResponse(m)


class ExportCustomOrder(generic.View):

    def get(self, request, *args, **kwargs):

        try:

            data = request.GET
            queryset = Order.objects.filter(customized_order=True)

            if data.get('checked_id'):
                order_id = data.get('checked_id').split(',')
                queryset = queryset.filter(id__in=order_id)

            if data.get('order_number'):
                queryset = queryset.filter(number__icontains=data.get('order_number'))

            if data.get('product'):
                product = data.get('product')
                order_line = OrderLine.objects.filter(product=product)
                queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

            excel_data = [
                [
                    'Sr. No', 'Order Number', 'Order value', 'Date placed', 'Order status'
                ]
            ]

            counter = 0

            for data in queryset:
                counter = counter + 1

                excel_data.append(
                    [
                        str(counter), str(data.number), str(data.total_incl_tax),
                        str(data.date_placed.date()), str(data.status)
                    ]
                )

            prms = {
                'type': 'excel',
                'filename': 'custom_order_%s' % (str(datetime.datetime.now())),
                'excel_data': excel_data
            }

            return generate_excel(request, **prms)

        except:

            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard')


@csrf_exempt
def get_products_order(request):

    product_list = []

    try:

        if request.is_ajax():

            data = request.GET

            search = data.get('term[term]')

            products = Product.objects.filter(is_approved='Approved', is_deleted=False)

            if data.getlist('exclude[]'):
                products = products.exclude(id__in=data.getlist('exclude[]'))

            if not request.user.is_superuser:
                vendor = Partner.objects.filter(users=request.user)
                stock = StockRecord.objects.filter(partner=vendor.last())
                products = products.filter(id__in=stock.values_list('product', flat=True))

            products = products.filter(Q(upc__icontains=search) | Q(title__icontains=search))

            for product in products:
                product_dict = dict()
                product_dict['id'] = product.id
                product_dict['itemName'] = product.title

                product_list.append(product_dict)

            return HttpResponse(json.dumps(product_list))

    except:

        return HttpResponse([])