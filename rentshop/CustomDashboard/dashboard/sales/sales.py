# python imports
import datetime

# django imports
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage

# packages imports
from oscar.core.loading import get_class, get_model

# internal import
from .sales_forms import *


_VendorCalender = get_model('partner', 'VendorCalender')
Partner = get_model('partner', 'Partner')
MultiDB = get_model('partner', 'MultiDB')
IndividualDB = get_model('partner', 'IndividualDB')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
Basket = get_model('basket', 'Basket')
BasketLine = get_model('basket', 'Line')
OrderAllocatedVendor = get_model('order', 'OrderAllocatedVendor')

VendorCalenderSearchForm1 = get_class('dashboard.forms', 'VendorCalenderSearchForm1')
generate_excel = get_class('dashboard.utils', 'generate_excel')
send_mail_core = get_class('promotions.utils', 'send_mail_core')
trigger_email = get_class('RentCore.tasks', 'trigger_email')
send_sms = get_class('RentCore.email', 'send_sms')


class OrderAllocateView(generic.View):

    template_name = 'dashboard/sales/prime_bucket/prime_order_details.html'

    def invalid_request(self, message):
        messages.error(self.request, message)
        return redirect(reverse('dashboard:index'))

    def get(self, request, *args, **kwargs):

        user = request.user
        order_number = self.kwargs.get('pk')

        # validate user
        if not user.is_active or not user.is_superuser:
            return self.invalid_request('Invalid request.')

        # validate order
        if not order_number or not Order.objects.filter(number=order_number):
            return self.invalid_request('Invalid order number.')

        order = Order.objects.get(number=order_number)
        order_lines = Line.objects.filter(order=order)

        context = dict()
        context['order'] = order
        context['order_lines'] = order_lines

        return render(self.request, self.template_name, context=context)


def allocate_vendor_sales(request):

    try:

        data = request.GET

        order_line_id = data.get('order_line_id')
        vendor_id = data.get('vendor_id')

        if not order_line_id or not vendor_id:
            messages.error(request, 'Invalid request. Try again.')
            return HttpResponse('SWR')

        _order_line = Line.objects.filter(id=order_line_id)
        _vendor = Partner.objects.filter(id=vendor_id)

        if not _order_line or not _vendor:
            messages.error(request, 'Invalid order details.')
            return HttpResponse('SWR')

        order_line = Line.objects.get(id=order_line_id)
        order = order_line.order

        product = order_line.product
        product_category = order_line.product.categories.last()

        vendor = Partner.objects.get(id=vendor_id)

        # check already allocate or not.
        _allocated = OrderAllocatedVendor.objects.filter(order_line=order_line)

        if _allocated:
            messages.error(request, 'Vendor already allocated.')
            return HttpResponse('SWR')

        allocation_data = {
            'order': order, 'order_line': order_line, 'order_number': order.number,
            'vendor': vendor, 'vendor_name': vendor.name,
            'product': product, 'product_category': product_category,
            'product_name': product.title, 'product_category_name': product_category.name
        }

        ol_obj = OrderAllocatedVendor.objects.create(**allocation_data)

        messages.success(
            request,
            '%s asp allocated to order #%s, Category %s' % (
                vendor.name, order.number, product_category.name
            )
        )

        # send email
        current_site = Site.objects.get_current()
        mail_data = {
            'mail_subject': 'Takerentpe : Order Allocated #%s' % (ol_obj.order_number),
            'mail_to': [vendor.email_id],
            'mail_template': 'dashboard/sales/prime_bucket/email_vendor_allocation.html',
            'mail_type': 'vendor_order_allocation',
            'allocated_obj_id': ol_obj.id,
            'domain': current_site.domain
        }
        trigger_email.delay(**mail_data)
        order_link = current_site.domain + '/dashboard/orders/' + str(ol_obj.order_number) + '/'

        #order booked sms
        message = 'You have received a new order for ' +  str(ol_obj.order_line.booking_start_date.date) +'-' + str(ol_obj.order_line.booking_end_date.date)+ ' Click on the link to check details of the order. '+'('+str(order_link)+')'+' Happy Celebranto!'
        msg_kwargs = {
            'message': message,
            'mobile_number': vendor.telephone_number,
        }
        send_sms(**msg_kwargs)

        return HttpResponse('200')

    except Exception as e:

        messages.error(request, 'Something went wrong.')
        return HttpResponse('IN_SERVER')


class SalesPrimeBucketView(generic.ListView):

    """
    Method to view sales orders.
    """

    template_name = 'dashboard/sales/prime_bucket/list.html'
    model = Order
    context_object_name = 'orders'
    paginate_by = 20
    form_class = SalesPrimeBucketSearchForm

    def get(self, request, *args, **kwargs):

        if not request.user.is_active:
            return redirect('/dashboard')

        return super(SalesPrimeBucketView, self).get(request, *args, **kwargs)

    def get_queryset(self):

        qs = self.model.objects.all()

        qs_line = Line.objects.all().exclude(order_type='Sale')
        qs = qs.filter(id__in=qs_line.values_list('order__id', flat=True), order_payment_status="success")
        exclude_qs = self.get_offer_orders(qs)
        qs = qs.exclude(id__in=exclude_qs.values('id'))

        data = self.request.GET

        if data.get('order_number'):
            qs = qs.filter(number__icontains=data.get('order_number'))

        return qs

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx

    def get_offer_orders(self, queryset):

        offer_lst = ['offer', 'Offer', 'offers', 'Offers']
        offers_cat = Category.objects.filter(name__in=offer_lst)
        offers_cat_list = []

        if offers_cat:
            offers_cat = offers_cat.last()
            offers_cat_list = list(offers_cat.get_descendants().values_list('name', flat=True))
            offers_cat_list.append(offers_cat.name)

        basket_lines = BasketLine.objects.filter(basket__id__in=queryset.values('basket_id'))
        basket_id_list = []
        for basket_line in basket_lines:
            if basket_line.product.categories.last():
                category_name_lst = list(
                    basket_line.product.categories.last().get_ancestors().values_list('name', flat=True))
                category_name_lst.append(basket_line.product.categories.last().name)

                if any(name in category_name_lst for name in offers_cat_list):
                    basket_id_list.append(basket_line.basket.id)
        exl_queryset = queryset.filter(basket_id__in=basket_id_list)
        return exl_queryset


class SalesListView(generic.ListView):

    """
    Method to view vendor calendar.
    """

    template_name = 'dashboard/sales/index.html'
    context_object_name = 'calendars'
    model = _VendorCalender
    queryset = _VendorCalender.objects.all()
    form_class = SalesSearchForm

    def get(self, request, *args, **kwargs):

        if not request.user.is_superuser:
            messages.error(request, 'Invalid request.')
            return redirect('/dashboard')

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        context = self.get_context_data()

        return self.render_to_response(context)

    def get_queryset(self):

        """
        Return vendor wise queryset
        :return: queryset
        """

        data = self.request.GET
        user = self.request.user

        if not self.form_class(data=self.request.GET).is_valid():
            messages.error(self.request, 'Please correct below errors.')
            return []

        queryset = self.model.objects.filter(product__is_deleted = False).order_by('-id')

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

        if data.get('upc'):
            upc = data.get('upc')
            queryset = queryset.filter(product__upc=upc)

        if data.get('vendor'):
            vendor = data.get('vendor')
            queryset = queryset.filter(vendor=vendor)

        if data.get('from_date') and data.get('to_date') is '':
            from_date = data.get('from_date')
            queryset = queryset.filter(from_date__date=from_date)

        if data.get('to_date') and data.get('from_date') is '':
            to_date = data.get('to_date')
            queryset = queryset.filter(to_date__date=to_date)

        if data.get('to_date') and data.get('from_date'):
            from_date = data.get('from_date')
            to_date = data.get('to_date')
            queryset = queryset.filter(
                from_date__date__gte=from_date,
                to_date__date__lte=to_date,
            )

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


def export_prime_bucket(request):

    """
    Method to export event
    :param request: default
    :return: xlsx:
    """

    try:

        data = request.GET

        queryset = Order.objects.all()
        qs_line = Line.objects.all().exclude(order_type='Sale')
        queryset = queryset.filter(id__in=qs_line.values_list('order__id', flat=True))
        offer_lst = ['offer', 'Offer', 'offers', 'Offers']
        offers_cat = Category.objects.filter(name__in=offer_lst)
        offers_cat_list = []

        if offers_cat:
            offers_cat = offers_cat.last()
            offers_cat_list = list(offers_cat.get_descendants().values_list('name', flat=True))
            offers_cat_list.append(offers_cat.name)

        basket_lines = BasketLine.objects.filter(basket__id__in=queryset.values('basket_id'))
        basket_id_list = []
        for basket_line in basket_lines:
            category_name_lst = list(
                basket_line.product.categories.last().get_ancestors().values_list('name', flat=True))
            category_name_lst.append(basket_line.product.categories.last().name)

            if any(name in category_name_lst for name in offers_cat_list):
                basket_id_list.append(basket_line.basket.id)
        exl_queryset = queryset.filter(basket_id__in=basket_id_list)
        queryset = queryset.exclude(id__in=exl_queryset.values('id'))

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('order_number'):
            order_number = data.get('order_number')
            queryset = queryset.filter(number__icontains=order_number)

        excel_data = [
            [
                'Sr. No', 'Order Number', 'Number of items', 'Allocated',
                'Date placed'
            ]
        ]

        counter = 0

        for row in queryset:

            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(row.number),
                    str(row.lines.count()), str(row.allocated_order.all().count()),
                    str(row.date_placed.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'prime_bucket_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return generate_excel(request, **prms)

    except Exception as e:

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


class SalesEventUpdateView(generic.View):

    """
    To update sales event.
    """

    template_name = 'dashboard/sales/form.html'
    form_class = VendorSaleCalendarAddEvent

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        vendor_event = _VendorCalender.objects.filter(id=pk)

        if not vendor_event:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=vendor_event.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        vendor_event = _VendorCalender.objects.filter(id=pk)

        if not vendor_event:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=vendor_event.last())

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()

        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/partners/sales/')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)


class SaleVendorDeleteEvent(generic.View):

    """
    delete asp event
    """

    template_name = 'dashboard/sales/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        vendor_event = _VendorCalender.objects.filter(id=pk)

        if not vendor_event:
            return self.invalid_request()

        context = dict()
        context['event'] = vendor_event.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            vendor_event = _VendorCalender.objects.filter(id=pk)

            if not vendor_event:
                return self.invalid_request()

            _VendorCalender.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/partners/sales')

        except:

            return self.invalid_request()


def export_bookedevents(request):

    """
    Method to export event
    :param request: default
    :return: xlsx:
    """

    try:

        data = request.GET

        queryset = _VendorCalender.objects.filter(product__is_deleted = False)

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('product'):
            product = data.get('product')
            queryset = queryset.filter(product=product)

        if data.get('upc'):
            upc = data.get('upc')
            queryset = queryset.filter(product__upc=upc)

        if data.get('vendor'):
            vendor = data.get('vendor')
            partner = Partner.objects.filter(id=vendor)
            queryset = queryset.filter(vendor__in=partner.values_list('id', flat=True))

        if data.get('from_date') and data.get('to_date') is '':
            from_date = data.get('from_date')
            queryset = queryset.filter(from_date__date=from_date)

        if data.get('to_date') and data.get('from_date') is '':
            to_date = data.get('to_date')
            queryset = queryset.filter(to_date__date=to_date)

        if data.get('to_date') and data.get('from_date'):
            from_date = data.get('from_date')
            to_date = data.get('to_date')
            queryset = queryset.filter(
                from_date__date__gte=from_date,
                to_date__date__lte=to_date,
            )

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
                'Sr. No', 'Product','ASP',  'From date', 'To date'
            ]
        ]

        counter = 0

        for calendar in queryset:

            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(calendar.product), str(calendar.vendor),str(calendar.from_date.date()),
                    str(calendar.to_date.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'bookedevent_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return generate_excel(request, **prms)

    except Exception as e:

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def sales_delete_bulk_event(request):

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


def re_allocate_vendor(request):

    try:

        data = request.GET

        order_line_id = data.get('order_line_id')
        vendor_id = data.get('vendor_id')

        if not order_line_id or not vendor_id:
            messages.error(request, 'Invalid request. Try again.')
            return HttpResponse('SWR')

        _order_line = Line.objects.filter(id=order_line_id)
        _vendor = Partner.objects.filter(id=vendor_id)

        if not _order_line or not _vendor:
            messages.error(request, 'Invalid order details.')
            return HttpResponse('SWR')

        order_line = Line.objects.get(id=order_line_id)
        order = order_line.order

        product = order_line.product
        product_category = order_line.product.categories.last()

        vendor = Partner.objects.get(id=vendor_id)

        # check already allocate or not.
        _allocated = OrderAllocatedVendor.objects.filter(order_line=order_line)

        if _allocated:
            #ORDER REALLOCATION SMS
            message = 'Order Reallocated: We have successfully moved the order  ' + str(order.number) + ' to another ASP. Happy Celebranto!'
            msg_kwargs = {
                'message': message,
                'mobile_number': _allocated.last().vendor.telephone_number,
            }
            send_sms(**msg_kwargs)

            OrderAllocatedVendor.objects.filter(
                order_line=order_line
            ).update(vendor = vendor, vendor_name=vendor.name)
            messages.success(request, 'Vendor re-allocated successfully.')
            ol_obj = _allocated.last()

        else:
            allocation_data = {
                'order': order, 'order_line': order_line, 'order_number': order.number,
                'vendor': vendor, 'vendor_name': vendor.name,
                'product': product, 'product_category': product_category,
                'product_name': product.title, 'product_category_name': product_category.name
            }

            ol_obj = OrderAllocatedVendor.objects.create(**allocation_data)
            messages.success(
                request,
                '%s asp allocated to order #%s, Category %s' % (
                    vendor.name, order.number, product_category.name
                )
            )
            

        # send email
        current_site = Site.objects.get_current()
        mail_data = {
            'mail_subject': 'Takerentpe : Order Allocated #%s' % (ol_obj.order_number),
            'mail_to': [vendor.email_id],
            'mail_template': 'dashboard/sales/prime_bucket/email_vendor_allocation.html',
            'mail_type': 'vendor_order_allocation',
            'allocated_obj_id': ol_obj.id,
            'domain': current_site.domain
        }
        trigger_email.delay(**mail_data)

        order_link = current_site.domain + '/dashboard/orders/' + str(ol_obj.order_number) + '/'

        # order booked sms
        message = 'You have received a new order for ' + str(ol_obj.order_line.booking_start_date.date()) + 'to' + str(
            ol_obj.order_line.booking_end_date.date()) + ' Click on the link to check details of the order. ' + '(' + str(
            order_link) + ')' + ' Happy Celebranto!'
        msg_kwargs = {
            'message': message,
            'mobile_number': vendor.telephone_number,
        }
        send_sms(**msg_kwargs)

        return HttpResponse('200')

    except Exception as e:

        messages.error(request, 'Something went wrong.')
        return HttpResponse('IN_SERVER')


class ReallocateOrderListView(generic.ListView):

    """
    Method to view sales orders.
    """

    template_name = 'dashboard/sales/prime_bucket/re_allocate_order/list.html'
    model = Order
    context_object_name = 'orders'
    paginate_by = 20
    form_class = SalesPrimeBucketSearchForm

    def get(self, request, *args, **kwargs):

        if not request.user.is_active:
            return redirect('/dashboard')

        return super(ReallocateOrderListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        allocated_orders = OrderAllocatedVendor.objects.all()
        qs = self.model.objects.filter(id__in=allocated_orders.values_list('order__id', flat=True))

        qs_line = Line.objects.all().exclude(order_type='Sale')
        qs = qs.filter(id__in=qs_line.values_list('order__id', flat=True), order_payment_status="success")
        exclude_qs = self.get_offer_orders(qs)
        qs = qs.exclude(id__in=exclude_qs.values('id'))

        data = self.request.GET

        if data.get('order_number'):
            qs = qs.filter(number__icontains=data.get('order_number'))

        return qs

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx

    def get_offer_orders(self, queryset):
        offer_lst = ['offer', 'Offer', 'offers', 'Offers']
        offers_cat = Category.objects.filter(name__in=offer_lst)
        offers_cat_list = []

        if offers_cat:
            offers_cat = offers_cat.last()
            offers_cat_list = list(offers_cat.get_descendants().values_list('name', flat=True))
            offers_cat_list.append(offers_cat.name)

        basket_lines = BasketLine.objects.filter(basket__id__in=queryset.values('basket_id'))
        basket_id_list = []
        try:
            for basket_line in basket_lines:
                category_name_lst = list(
                    basket_line.product.categories.last().get_ancestors().values_list('name', flat=True))
                category_name_lst.append(basket_line.product.categories.last().name)

                if any(name in category_name_lst for name in offers_cat_list):
                    basket_id_list.append(basket_line.basket.id)
        except:
            exl_queryset = queryset.filter(basket_id__in=basket_id_list)
        return exl_queryset


class OrderReallocateView(generic.View):

    template_name = 'dashboard/sales/prime_bucket/re_allocate_order/details.html'

    def invalid_request(self, message):
        messages.error(self.request, message)
        return redirect(reverse('dashboard:index'))

    def get(self, request, *args, **kwargs):

        user = request.user
        order_number = self.kwargs.get('pk')

        # validate user
        if not user.is_active or not user.is_superuser:
            return self.invalid_request('Invalid request.')

        # validate order
        if not order_number or not Order.objects.filter(number=order_number):
            return self.invalid_request('Invalid order number.')

        order = Order.objects.get(number=order_number)
        order_lines = Line.objects.filter(order=order)
        allocated_vendor = OrderAllocatedVendor.objects.filter(order_line__in=order_lines)
        context = dict()
        context['order'] = order
        context['order_lines'] = order_lines
        context['allocated_vendor'] = allocated_vendor

        return render(request, self.template_name, context=context)


class CancelledOrderListView(generic.ListView):

    """
    Method to view sales orders.
    """

    template_name = 'dashboard/sales/cancelled_order/list.html'
    model = Order
    context_object_name = 'orders'
    paginate_by = 20
    form_class = SalesPrimeBucketSearchForm

    def get(self, request, *args, **kwargs):

        if not request.user.is_active:
            return redirect('/dashboard')

        return super(CancelledOrderListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # allocated_orders = Order.objects.filter()
        qs = self.model.objects.filter(status = "Cancelled")

        # qs_line = Line.objects.all().exclude(order_type='Sale')
        # qs = qs.filter(id__in=qs_line.values_list('order__id', flat=True))

        data = self.request.GET

        if data.get('order_number'):
            qs = qs.filter(number__icontains=data.get('order_number'))

        return qs

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx


class ChangeOrderStatus(generic.View):

    def get(self, request, *args, **kwargs):

        try:
            amount = 0
            data = request.GET

            order_id = data.get('order_id')

            Order.objects.get(id=order_id)
            order_obj = Order.objects.filter(id=order_id)
            if order_obj and order_obj.last().user and order_obj.last().refund_amount:
                order = order_obj.last()
                current_site = Site.objects.get_current()
                mail_subject = 'TakeRentPe -  Refund Amount.'
                message = render_to_string(
                    'customer/email/order_refunded_email.html',
                    {
                        'user': order.user,
                        'number': order.number,
                        'deposite_amount': str(order.refund_amount),
                        'domain': current_site.domain,
                    }
                )

                to_email = order.user.email,
                from_email = settings.FROM_EMAIL_ADDRESS
                email = EmailMessage(mail_subject, message, from_email, to_email)
                email.content_subtype = "html"
                email.send()
                Order.objects.filter(id=order_id).update(is_refund=True)

                return HttpResponse('200')

            return HttpResponse('201')

        except Exception as e:
            import os
            import sys
            print('-----------in exception----------')
            print(e.args)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            messages.error(request, 'Something went wrong.')
            return HttpResponse('500')


class OffersPrimeBucketView(generic.ListView):

    """
    Method to view sales orders.
    """

    template_name = 'dashboard/sales/offers_prime_bucket/list.html'
    model = Order
    context_object_name = 'orders'
    paginate_by = 20
    form_class = SalesPrimeBucketSearchForm

    def get(self, request, *args, **kwargs):

        if not request.user.is_active:
            return redirect('/dashboard')

        return super(OffersPrimeBucketView, self).get(request, *args, **kwargs)

    def get_queryset(self):

        qs = self.model.objects.all()

        qs_line = Line.objects.all().exclude(order_type='Sale')
        qs = qs.filter(id__in=qs_line.values_list('order__id', flat=True), order_payment_status="success")
        offers_qs = self.get_offer_orders(qs)
        qs = qs.filter(id__in=offers_qs.values('id'))

        data = self.request.GET

        if data.get('order_number'):
            qs = qs.filter(number__icontains=data.get('order_number'))

        return qs

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx

    def get_offer_orders(self, queryset):
        offer_lst = ['offer', 'Offer', 'offers', 'Offers']
        offers_cat = Category.objects.filter(name__in=offer_lst)
        offers_cat_list = []

        if offers_cat:
            offers_cat = offers_cat.last()
            offers_cat_list = list(offers_cat.get_descendants().values_list('name', flat=True))
            offers_cat_list.append(offers_cat.name)

        basket_lines = BasketLine.objects.filter(basket__id__in=queryset.values('basket_id'))
        basket_id_list = []
        ###### alteration if query didn't able to execute
        try:
            for basket_line in basket_lines:
                category_name_lst = list(
                    basket_line.product.values_list('name', flat=True))
                category_name_lst.append(basket_line.product.categories.last().name)


            if any(name in category_name_lst for name in offers_cat_list):
                basket_id_list.append(basket_line.basket.id)
        except:
            offers_queryset = queryset.filter(basket_id__in=basket_id_list)
            return offers_queryset


class OffersOrderReallocate(generic.ListView):

    """
    Method to view sales orders.
    """

    template_name = 'dashboard/sales/offers_prime_bucket/reallocate.html'
    model = Order
    context_object_name = 'orders'
    paginate_by = 20
    form_class = SalesPrimeBucketSearchForm

    def get(self, request, *args, **kwargs):

        if not request.user.is_active:
            return redirect('/dashboard')

        return super(OffersOrderReallocate, self).get(request, *args, **kwargs)

    def get_queryset(self):
        allocated_orders = OrderAllocatedVendor.objects.all()
        qs = self.model.objects.filter(id__in=allocated_orders.values_list('order__id', flat=True))
        
        qs_line = Line.objects.all().exclude(order_type='Sale')
        qs = qs.filter(id__in=qs_line.values_list('order__id', flat=True), order_payment_status="success")

        offers_qs = self.get_offer_orders(qs)
        qs = qs.filter(id__in=offers_qs.values('id'))

        data = self.request.GET

        if data.get('order_number'):
            qs = qs.filter(number__icontains=data.get('order_number'))

        return qs

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx

    def get_offer_orders(self, queryset):
        offer_lst = ['offer', 'Offer', 'offers', 'Offers']
        offers_cat = Category.objects.filter(name__in=offer_lst)
        offers_cat_list = []

        if offers_cat:
            offers_cat = offers_cat.last()
            offers_cat_list = list(offers_cat.get_descendants().values_list('name', flat=True))
            offers_cat_list.append(offers_cat.name)

        basket_lines = BasketLine.objects.filter(basket__id__in=queryset.values('basket_id'))
        basket_id_list = []
        try:
            for basket_line in basket_lines:
                category_name_lst = list(basket_line.product.categories.last().get_ancestors().values_list('name', flat=True))
                category_name_lst.append(basket_line.product.categories.last().name)

                if any(name in category_name_lst for name in offers_cat_list):
                    basket_id_list.append(basket_line.basket.id)
        except:
            offers_queryset = queryset.filter(basket_id__in=basket_id_list)
            return offers_queryset


def export_offers_prime_bucket(request):

    """
    Method to export event
    :param request: default
    :return: xlsx:
    """

    try:

        data = request.GET

        queryset = Order.objects.all()
        qs_line = Line.objects.all().exclude(order_type='Sale')
        queryset = queryset.filter(id__in=qs_line.values_list('order__id', flat=True))
        offer_lst = ['offer', 'Offer', 'offers', 'Offers']
        basket_lines = BasketLine.objects.filter(basket__id__in=queryset.values('basket_id'))
        basket_id_list = []
        for basket_line in basket_lines:
            category_name_lst = list(
                basket_line.product.categories.last().get_ancestors().values_list('name', flat=True))
            category_name_lst.append(basket_line.product.categories.last().name)
            if any(name in category_name_lst for name in offer_lst):
                basket_id_list.append(basket_line.basket.id)
        offers_queryset = queryset.filter(basket_id__in=basket_id_list)

        queryset = queryset.filter(id__in=offers_queryset.values('id'))

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('order_number'):
            order_number = data.get('order_number')
            queryset = queryset.filter(number__icontains=order_number)

        excel_data = [
            [
                'Sr. No', 'Order Number', 'Number of items', 'Allocated',
                'Date placed'
            ]
        ]

        counter = 0

        for row in queryset:

            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(row.number),
                    str(row.lines.count()), str(row.allocated_order.all().count()),
                    str(row.date_placed.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'offers_prime_bucket_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return generate_excel(request, **prms)

    except Exception as e:

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


class OffersOrderAllocateView(generic.View):

    template_name = 'dashboard/sales/offers_prime_bucket/details.html'

    def invalid_request(self, message):
        messages.error(self.request, message)
        return redirect(reverse('dashboard:index'))

    def get(self, request, *args, **kwargs):

        user = request.user
        order_number = self.kwargs.get('pk')

        # validate user
        if not user.is_active or not user.is_superuser:
            return self.invalid_request('Invalid request.')

        # validate order
        if not order_number or not Order.objects.filter(number=order_number):
            return self.invalid_request('Invalid order number.')

        order = Order.objects.get(number=order_number)
        order_lines = Line.objects.filter(order=order)

        context = dict()
        context['order'] = order
        context['order_lines'] = order_lines

        return render(self.request, self.template_name, context=context)


class OffersOrderReallocateView(generic.View):

    template_name = 'dashboard/sales/offers_prime_bucket/reallocate_details.html'

    def invalid_request(self, message):
        messages.error(self.request, message)
        return redirect(reverse('dashboard:index'))

    def get(self, request, *args, **kwargs):

        user = request.user
        order_number = self.kwargs.get('pk')

        # validate user
        if not user.is_active or not user.is_superuser:
            return self.invalid_request('Invalid request.')

        # validate order
        if not order_number or not Order.objects.filter(number=order_number):
            return self.invalid_request('Invalid order number.')

        order = Order.objects.get(number=order_number)
        order_lines = Line.objects.filter(order=order)
        allocated_vendor = OrderAllocatedVendor.objects.filter(order_line__in=order_lines)
        context = dict()
        context['order'] = order
        context['order_lines'] = order_lines
        context['allocated_vendor'] = allocated_vendor

        return render(request, self.template_name, context=context)

