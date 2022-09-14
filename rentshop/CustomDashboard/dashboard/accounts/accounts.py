# python imports
import datetime, json

# django imports
from django.db.models import Sum
from django.views.generic import TemplateView, View, ListView
from django.shortcuts import *
from django.contrib import messages
from django.db.models import Q

# packages imports
from oscar.core.loading import *
from oscar.apps.dashboard.views import IndexView
from oscar.core.compat import get_user_model

# internal imports
from .. import utils
from .accounts_forms import *

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
Order = get_model('order', 'Order')
User = get_user_model()


def calculate_order_stats(queryset):

    return {
        'count': queryset.count(),
        'total': queryset.filter(total_excl_tax__isnull=False).aggregate(Sum('total_excl_tax')).get('total_excl_tax__sum'),
        'margin': queryset.filter(order_margin_price__isnull=False).aggregate(Sum('order_margin_price')).get('order_margin_price__sum'),
    }


class ApplyMarginView(View):

    def get(self, request, *args, **kwargs):

        try:

            data = request.GET

            margin_value = data.get('margin_value')
            product_id = data.get('product_id')

            Product.objects.get(id=product_id)
            Product.objects.filter(id=product_id).update(product_margin=margin_value)

            return HttpResponse('200')

        except:

            messages.error(request, 'Something went wrong.')
            return HttpResponse('500')


class SetMarginListView(ListView):

    template_name = 'dashboard/accounts/margin/set_margin_list.html'
    form = SetProductMarginForm
    model = Product
    paginate_by = 20
    context_object_name = 'products'

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form(self.request.GET)

        return ctx

    def get_queryset(self):

        category_list, qs = [], []

        context = dict()

        data = self.request.GET

        if data.get('product_name') or data.get('upc') or data.get('category') or data.get('sub_category'):
            qs = Product.objects.filter(is_deleted = False)

        if data.get('product_name'):
            qs = qs.filter(title__icontains=data.get('product_name'))

        if data.get('upc'):
            qs = qs.filter(upc__icontains=data.get('upc'))

        if data.get('category') and data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            qs = qs.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        return qs


class AccountNetProfitView(TemplateView):

    template_name = 'dashboard/accounts/net_profile/index.html'
    form_class = AccountSearchForm

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or not user.is_superuser:
            messages.error(request, 'Invalid request.')
            return redirect('/dashborad')

        return super(AccountNetProfitView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_order_stats())
        ctx['form'] = self.form_class()

        return ctx

    def get_order_stats(self):

        data = self.request.GET

        daily_order_count, daily_order_total, daily_order_margin_total, daily_order_earning_total = 0, 0, 0, 0
        weekly_order_count, weekly_order_total, weekly_order_margin_total, weekly_order_earning_total = 0, 0, 0, 0
        monthly_order_count, monthly_order_total, monthly_order_margin_total, monthly_order_earning_total = 0, 0, 0, 0
        quarterly_order_count, quarterly_order_total, quarterly_order_margin_total, quarterly_order_earning_total = 0, 0, 0, 0
        yearly_order_count, yearly_order_total, yearly_order_margin_total, yearly_order_earning_total = 0, 0, 0, 0

        today = datetime.datetime.now()
        last_week = today.date() - datetime.timedelta(days=7)
        last_month = today.date() - datetime.timedelta(days=20)
        quarterly_month = today.date() - datetime.timedelta(days=90)
        yearly_month = today.date() - datetime.timedelta(days=365)

        orders = Order.objects.all()

        daily_orders = orders.filter(date_placed__date=today)

        if data.get('record_type') == 'daily' and data.get('order_number'):
            daily_orders = daily_orders.filter(number__icontains=data.get('order_number'))

        if data.get('record_type') == 'daily' and data.get('customer_name'):
            daily_orders = daily_orders.filter(Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

        if data.get('record_type') == 'daily' and data.get('order_date'):
            daily_orders = daily_orders.filter(date_placed__date=data.get('order_date'))

        daily_data = calculate_order_stats(daily_orders)
        daily_order_count = daily_data.get('count')
        daily_order_total = daily_data.get('total')
        daily_order_earning_total = daily_data.get('margin')

        weekly_orders = orders.filter(date_placed__date__gte=last_week)

        if data.get('record_type') == 'weekly' and data.get('order_number'):
            weekly_orders = weekly_orders.filter(number__icontains=data.get('order_number'))

        if data.get('record_type') == 'weekly' and data.get('customer_name'):
            weekly_orders = weekly_orders.filter(Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

        if data.get('record_type') == 'weekly' and data.get('order_date'):
            weekly_orders = weekly_orders.filter(date_placed__date=data.get('order_date'))

        weekly_data = calculate_order_stats(weekly_orders)

        weekly_order_count = weekly_data.get('count')
        weekly_order_total = weekly_data.get('total')
        weekly_order_earning_total = weekly_data.get('margin')

        monthly_orders = orders.filter(date_placed__date__gte=last_month)

        if data.get('record_type') == 'monthly' and data.get('order_number'):
            monthly_orders = monthly_orders.filter(number__icontains=data.get('order_number'))

        if data.get('record_type') == 'monthly' and data.get('customer_name'):
            monthly_orders = weekly_orders.filter(Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

        if data.get('record_type') == 'monthly' and data.get('order_date'):
            monthly_orders = monthly_orders.filter(date_placed__date=data.get('order_date'))

        monthly_data = calculate_order_stats(monthly_orders)

        monthly_order_count = monthly_data.get('count')
        monthly_order_total = monthly_data.get('total')
        monthly_order_earning_total = monthly_data.get('margin')

        quarterly_orders = orders.filter(date_placed__date__gte=quarterly_month)

        if data.get('record_type') == 'quarterly' and data.get('order_number'):
            quarterly_orders = quarterly_orders.filter(number__icontains=data.get('order_number'))

        if data.get('record_type') == 'quarterly' and data.get('customer_name'):
            quarterly_orders = quarterly_orders.filter(Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

        if data.get('record_type') == 'quarterly' and data.get('order_date'):
            quarterly_orders = quarterly_orders.filter(date_placed__date=data.get('order_date'))

        quarterly_data = calculate_order_stats(quarterly_orders)

        quarterly_order_count = quarterly_data.get('count')
        quarterly_order_total = quarterly_data.get('total')
        quarterly_order_earning_total = quarterly_data.get('margin')

        yearly_orders = orders.filter(date_placed__date__gte=yearly_month)

        if data.get('record_type') == 'yearly' and data.get('order_number'):
            yearly_orders = yearly_orders.filter(number__icontains=data.get('order_number'))

        if data.get('record_type') == 'yearly' and data.get('customer_name'):
            yearly_orders = yearly_orders.filter(Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

        if data.get('record_type') == 'yearly' and data.get('order_date'):
            yearly_orders = yearly_orders.filter(date_placed__date=data.get('order_date'))

        yearly_data = calculate_order_stats(yearly_orders)

        yearly_order_count = yearly_data.get('count')
        yearly_order_total = yearly_data.get('total')
        yearly_order_earning_total = yearly_data.get('margin')

        return {
            'daily_orders': daily_orders,
            'daily_order_count': daily_order_count,
            'daily_order_total': daily_order_total,
            'daily_order_earning_total': daily_order_earning_total,

            'weekly_orders': weekly_orders,
            'weekly_order_count': weekly_order_count,
            'weekly_order_total': weekly_order_total,
            'weekly_order_margin_total': weekly_order_margin_total,
            'weekly_order_earning_total': weekly_order_earning_total,

            'monthly_orders': monthly_orders,
            'monthly_order_count': monthly_order_count,
            'monthly_order_total': monthly_order_total,
            'monthly_order_margin_total': monthly_order_margin_total,
            'monthly_order_earning_total': monthly_order_earning_total,

            'quarterly_orders': quarterly_orders,
            'quarterly_order_count': quarterly_order_count,
            'quarterly_order_total': quarterly_order_total,
            'quarterly_order_margin_total': quarterly_order_margin_total,
            'quarterly_order_earning_total': quarterly_order_earning_total,

            'yearly_orders': yearly_orders,
            'yearly_order_count': yearly_order_count,
            'yearly_order_total': yearly_order_total,
            'yearly_order_margin_total': yearly_order_margin_total,
            'yearly_order_earning_total': yearly_order_earning_total,
        }


class ExportNetProfile(View):

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        data = request.GET

        stats = AccountNetProfitView.get_order_stats(self)

        order_count, order_total, order_earning = 0, 0, 0

        excel_data = [
            [
               'Orders', 'Order Total (Rs)', 'Order Total Earning (Rs)'
            ]
        ]

        if pk == '1':

            query = stats.get('daily_orders')

            if data.get('record_type') == 'daily' and data.get('order_number'):
                query = query.filter(number__icontains=data.get('order_number'))

            if data.get('record_type') == 'daily' and data.get('customer_name'):
                query = query.filter(
                    Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

            if data.get('record_type') == 'daily' and data.get('order_date'):
                query = query.filter(date_placed__date=data.get('order_date'))

            daily_data = calculate_order_stats(query)

            if daily_data:

                order_count = daily_data.get('count')
                order_total = daily_data.get('total')
                order_earning = daily_data.get('margin')

            excel_data.append([order_count, order_total, order_earning])
            excel_data.append(['Order number', 'Customer', 'Total Amount', 'Number of items', 'Shipping address', 'Date of purchase', 'Status', 'Payment Status'])

            for qs in query:

                excel_data.append([str(qs.number), str(qs.user.first_name), str(qs.total_incl_tax), str(qs.num_items), str(qs.shipping_address), str(qs.date_placed), str(qs.status), str(qs.get_order_payment_status_display())])

        if pk == '2':

            query = stats.get('weekly_orders')

            if data.get('record_type') == 'weekly' and data.get('order_number'):
                query = query.filter(number__icontains=data.get('order_number'))

            if data.get('record_type') == 'weekly' and data.get('customer_name'):
                query = query.filter(
                    Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

            if data.get('record_type') == 'weekly' and data.get('order_date'):
                query = query.filter(date_placed__date=data.get('order_date'))

            daily_data = calculate_order_stats(query)

            if daily_data:
                order_count = daily_data.get('count')
                order_total = daily_data.get('total')
                order_earning = daily_data.get('margin')

            excel_data.append([order_count, order_total, order_earning])
            excel_data.append(['Order number', 'Customer', 'Total Amount', 'Number of items', 'Shipping address', 'Date of purchase', 'Status', 'Payment Status'])

            for qs in query:
                if not qs.user:
                    first_name= ''
                else:
                    first_name = qs.user.first_name
                excel_data.append([str(qs.number), str(first_name), str(qs.total_incl_tax), str(qs.num_items), str(qs.shipping_address), str(qs.date_placed), str(qs.status), str(qs.get_order_payment_status_display())])

        if pk == '3':

            query = stats.get('monthly_orders')

            if data.get('record_type') == 'monthly' and data.get('order_number'):
                query = query.filter(number__icontains=data.get('order_number'))

            if data.get('record_type') == 'monthly' and data.get('customer_name'):
                query = query.filter(
                    Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

            if data.get('record_type') == 'monthly' and data.get('order_date'):
                query = query.filter(date_placed__date=data.get('order_date'))

            daily_data = calculate_order_stats(query)

            if daily_data:
                order_count = daily_data.get('count')
                order_total = daily_data.get('total')
                order_earning = daily_data.get('margin')

            excel_data.append([order_count, order_total, order_earning])
            excel_data.append(
                ['Order number', 'Customer', 'Total Amount', 'Number of items', 'Shipping address', 'Date of purchase',
                 'Status', 'Payment Status'])

            for qs in query:
                if not qs.user:
                    first_name= ''
                else:
                    first_name = qs.user.first_name
                excel_data.append([str(qs.number), str(first_name), str(qs.total_incl_tax), str(qs.num_items),
                                   str(qs.shipping_address), str(qs.date_placed), str(qs.status),
                                   str(qs.get_order_payment_status_display())])

        if pk == '4':

            query = stats.get('quarterly_orders')

            if data.get('record_type') == 'quarterly' and data.get('order_number'):
                query = query.filter(number__icontains=data.get('order_number'))

            if data.get('record_type') == 'quarterly' and data.get('customer_name'):
                query = query.filter(
                    Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

            if data.get('record_type') == 'quarterly' and data.get('order_date'):
                query = query.filter(date_placed__date=data.get('order_date'))

            daily_data = calculate_order_stats(query)

            if daily_data:
                order_count = daily_data.get('count')
                order_total = daily_data.get('total')
                order_earning = daily_data.get('margin')

            excel_data.append([order_count, order_total, order_earning])
            excel_data.append(
                ['Order number', 'Customer', 'Total Amount', 'Number of items', 'Shipping address', 'Date of purchase',
                 'Status', 'Payment Status'])

            for qs in query:
                if not qs.user:
                    first_name= ''
                else:
                    first_name = qs.user.first_name
                excel_data.append([str(qs.number), str(first_name), str(qs.total_incl_tax), str(qs.num_items),
                                   str(qs.shipping_address), str(qs.date_placed), str(qs.status),
                                   str(qs.get_order_payment_status_display())])

        if pk == '5':

            query = stats.get('yearly_orders')

            if data.get('record_type') == 'yearly' and data.get('order_number'):
                query = query.filter(number__icontains=data.get('order_number'))

            if data.get('record_type') == 'yearly' and data.get('customer_name'):
                query = query.filter(
                    Q(user__first_name=data.get('customer_name')) | Q(user__last_name=data.get('customer_name')))

            if data.get('record_type') == 'yearly' and data.get('order_date'):
                query = query.filter(date_placed__date=data.get('order_date'))

            daily_data = calculate_order_stats(query)

            if daily_data:
                order_count = daily_data.get('count')
                order_total = daily_data.get('total')
                order_earning = daily_data.get('margin')

            excel_data.append([order_count, order_total, order_earning])
            excel_data.append(
                ['Order number', 'Customer', 'Total Amount', 'Number of items', 'Shipping address', 'Date of purchase',
                 'Status', 'Payment Status'])

            for qs in query:
                if not qs.user:
                    first_name= ''
                else:
                    first_name = qs.user.first_name
                excel_data.append([str(qs.number), str(first_name), str(qs.total_incl_tax), str(qs.num_items),
                                   str(qs.shipping_address), str(qs.date_placed), str(qs.status),
                                   str(qs.get_order_payment_status_display())])

        prms = {
            'type': 'excel',
            'filename': 'net_profit_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)


class ProductMarginListView(ListView):

    template_name = 'dashboard/accounts/margin/list.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 20
    form_class = ProductMarginSearchForm

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_active or not request.user.is_superuser:
            messages.error(request, 'Invalid request')
            return redirect('/dashboard')

        return super(ProductMarginListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):

        data = self.request.GET

        qs = self.model.objects.filter(is_approved='Approved', is_deleted = False)
        category_list = []

        if data.get('product_name'):
            qs = qs.filter(title__icontains=data.get('product_name'))

        if data.get('upc'):
            qs = qs.filter(upc__icontains=data.get('upc'))

        if data.get('category') and data.get('sub_category'):

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            qs = qs.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('vendor_name'):
            partner = Partner.objects.filter(name__icontains=data.get('vendor_name'))
            stock_record = StockRecord.objects.filter(partner__id__in=partner.values_list('id', flat=True))
            qs = qs.filter(id__in=stock_record.values_list('product', flat=True))

        return qs

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class()

        return ctx


class GetSubCategory(View):

    def get(self, request, *args, **kwargs):

        depth_2 = []
        main_category_id = request.GET.get('category')

        depth_1 = Category.objects.get(id=main_category_id)

        for category in depth_1.get_children():

            depth_2_dict = dict()
            depth_2_dict['id'] = category.id
            depth_2_dict['text'] = category.name

            depth_2.append(depth_2_dict)

        return HttpResponse(json.dumps(depth_2))
