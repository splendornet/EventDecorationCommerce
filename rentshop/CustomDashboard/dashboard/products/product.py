# python imports
import datetime, json

# django imports
from django.views import generic
from django.db.models import Q
from django.shortcuts import redirect, HttpResponse, render, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

# packages imports
from oscar.apps.dashboard.catalogue.views import ProductListView
from oscar.core.loading import get_class, get_model

# internal imports
from .product_forms import *
from .product_formset import *
from .. import utils

Product = get_model('catalogue', 'Product')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')
Partner = get_model('partner', 'Partner')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'Category')
ProductImage = get_model('catalogue', 'ProductImage')
StockRecord = get_model('partner', 'StockRecord')

ProductTable = get_class('dashboard.tables', 'CustomProductTable')
CustomProductSearchForm = get_class('dashboard.forms','CustomProductSearchForm')


class RateCardListView(generic.ListView):

    """
    Method to display product rate cards.
    """

    template_name = 'dashboard/rate_card/products/list.html'
    model = ProductCostEntries
    paginate_by = 20
    context_object_name = 'products'
    search_form = RateCardProductSearchForm

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        return super(RateCardListView, self).get(request, *args, **kwargs)

    def get_queryset(self):

        """
        Returns queryset
        :return: qs
        """

        data = self.request.GET

        qs_cost_product = self.model.objects.filter(is_deleted=False).values_list('product', flat=True).distinct()
        qs = Product.objects.filter(id__in=qs_cost_product, product_cost_type='Multiple',is_deleted=False)

        if data.get('product_upc'):
            qs = qs.filter(upc__icontains=data.get('product_upc'))

        if data.get('category') and data.get('sub_category'):

            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            qs = qs.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            qs = qs.filter(categories__in=id_list)

            # qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('product'):
            qs = qs.filter(id=data.get('product'))

        if data.get('transport_available'):

            transport_available = False

            if data.get('transport_available') == '1':
                transport_available = True

            qs = qs.filter(is_transporation_available=transport_available)

        return qs

    def get_context_data(self, **kwargs):

        """
        Return context data
        :param kwargs: dict
        :return: dict
        """

        ctx = super(RateCardListView, self).get_context_data(**kwargs)

        ctx['form'] = self.search_form(data=self.request.GET)

        return ctx


class RateCardDetailListView(generic.ListView):

    """
    Method to display product rate cards.
    """

    template_name = 'dashboard/rate_card/products/detail_list.html'
    model = ProductCostEntries
    paginate_by = 20
    context_object_name = 'products'
    search_form = RateCardProductSearchForm

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        return super(RateCardDetailListView, self).get(request, *args, **kwargs)

    def get_queryset(self):

        """
        Returns queryset
        :return: qs
        """

        data = self.request.GET

        pk = self.kwargs.get('pk')

        product = Product.objects.filter(id=pk,is_deleted=False).last()
        qs = self.model.objects.filter(product=product, is_deleted=False).exclude(quantity_from__isnull= True, quantity_to__isnull = True, rent_quantity_from__isnull = True ,rent_quantity_to__isnull = True)

        if data.get('product_upc'):
            qs = qs.filter(upc__icontains=data.get('product_upc'))

        if data.get('product'):
            qs = qs.filter(id=data.get('product'))

        return qs

    def get_context_data(self, **kwargs):

        """
        Return context data
        :param kwargs: dict
        :return: dict
        """

        ctx = super(RateCardDetailListView, self).get_context_data(**kwargs)

        pk = self.kwargs.get('pk')

        product = Product.objects.filter(id=pk,is_deleted=False).last()

        ctx['form'] = self.search_form(data=self.request.GET)
        ctx['product'] = product

        return ctx


class RateCardCreateView(generic.View):

    """
    Method to create product rate card.
    """

    template_name = 'dashboard/rate_card/products/form.html'
    formset = BaseProductCostEntriesSet_Create

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context, product = dict(), None

        user = request.user
        product_id = self.request.GET.get('product')

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if ProductCostEntries.objects.filter(product__id=product_id):
            return self.invalid_request('Select valid product.')

        try:
            product = Product.objects.get(id=product_id)
            if user.is_staff and not user.is_superuser:
                vendor = Partner.objects.get(users=user)
                stock = StockRecord.objects.filter(product=product, partner=vendor)
                if not stock:
                    return self.invalid_request('Something went wrong.')
        except:
            return self.invalid_request('Something went wrong.')

        context['product'] = product
        context['form_type'] = '1'
        context['formset'] = self.formset(form_kwargs={'base_product': product.id})

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        product_id = self.request.GET.get('product')
        product = Product.objects.get(id=product_id)
        count = 0
        msg = None
        formset = self.formset(request.POST, form_kwargs={'base_product': product.id})

        if not formset.is_valid():
            return self.is_invalid(formset)

        if ProductCostEntries.objects.filter(product=product):
            return self.invalid_request('Invalid product.')

        for form in formset:

            if form.is_valid():

                try:
                    if form.cleaned_data.get('quantity_from') != None and form.cleaned_data.get('quantity_to') != None or form.cleaned_data.get('rent_quantity_from') != None and form.cleaned_data.get('rent_quantity_to') != None:
                        base = form.save(commit=False)
                        base.product_upc = product.upc
                        base.product_type = product.product_class.name
                        base.save()
                        count = 1
                except:
                    pass
        if count:
            msg = 'Costing for %s saved successfully.' % (product.title)
        else:
            msg = 'Empty data not saved'
        messages.success(self.request, msg)
        return HttpResponseRedirect(reverse('dashboard:rate-card-products'))

    def is_invalid(self, formset):

        context, product = dict(), None

        product_id = self.request.GET.get('product')
        product = Product.objects.get(id=product_id)

        context['product'] = product
        context['formset'] = formset
        context['form_type'] = '1'

        messages.error(self.request, 'Please correct below errors.')
        return render(self.request, self.template_name, context=context)


class RateCardUpdateView(generic.View):

    """
    Method to create product rate card.
    """

    template_name = 'dashboard/rate_card/products/form.html'
    formset = BaseProductCostEntriesSet

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context, product = dict(), None

        user = request.user
        product_id = self.kwargs.get('pk')

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not ProductCostEntries.objects.filter(product__id=product_id):
            return self.invalid_request('Select valid product.')

        try:
            product = Product.objects.get(id=product_id)
            if user.is_staff and not user.is_superuser:
                vendor = Partner.objects.get(users=user)
                stock = StockRecord.objects.filter(product=product, partner=vendor)
                if not stock:
                    return self.invalid_request('Something went wrong.')
        except:
            return self.invalid_request('Something went wrong.')

        product_costs = ProductCostEntries.objects.filter(product=product)

        context['product'] = product
        context['formset'] = self.formset(queryset=product_costs, form_kwargs={'base_product': product.id})

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        product_id = kwargs.get('pk')
        product = Product.objects.get(id=product_id)

        formset = self.formset(request.POST, form_kwargs={'base_product': product.id})

        if not formset.is_valid():
            return self.is_invalid(formset)

        if not ProductCostEntries.objects.filter(product=product):
            return self.invalid_request('Invalid product.')

        for form in formset:

            if form.is_valid():

                try:
                    if form.cleaned_data.get('quantity_from') != None and form.cleaned_data.get('quantity_to') != None or form.cleaned_data.get('rent_quantity_from') != None and form.cleaned_data.get('rent_quantity_to') != None:
                        base = form.save(commit=False)
                        base.product_upc = product.upc
                        base.product_type = product.product_class.name
                        base.save()
                except:
                    pass

        messages.success(self.request, 'Costing for %s updated successfully.' % (product.title))
        return HttpResponseRedirect(reverse('dashboard:rate-card-products'))

    def is_invalid(self, formset):

        context, product = dict(), None

        product_id = self.kwargs.get('pk')
        product = Product.objects.get(id=product_id)

        context['product'] = product
        context['formset'] = formset

        messages.error(self.request, 'Please correct below errors.')
        return render(self.request, self.template_name, context=context)


class RateCardDeleteView(generic.View):

    """
    Method to delete rate card.
    """

    template_name = 'dashboard/rate_card/products/delete.html'

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context = dict()

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not Product.objects.filter(id=pk,is_deleted=False):
            return self.invalid_request('Select valid product.')

        product = Product.objects.get(id=pk)

        context['product'] = product

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not Product.objects.filter(id=pk,is_deleted=False):
            return self.invalid_request('Select valid product.')

        product = Product.objects.get(id=pk)
        ProductCostEntries.objects.filter(product=product).delete()

        messages.success(request, 'Record delete succesfully.')
        return HttpResponseRedirect(reverse('dashboard:rate-card-products'))


class FilteredProductListView(ProductListView):

    """
    Oscar extended product list view.
    """

    table_class = ProductTable
    form_class = CustomProductSearchForm

    def get_queryset(self):

        try:

            if self.request.user.is_superuser:
                queryset = Product.browsable.base_queryset()
                queryset = self.filter_queryset(queryset)
                queryset = self.apply_search(queryset)
                queryset = queryset.filter(is_deleted = False)
                if ProductClass.objects.filter(name='Combo'):
                    combo_class = ProductClass.objects.filter(name='Combo').last()
                    queryset = queryset.exclude(product_class=combo_class)
                return queryset
            else:
                qs = super(FilteredProductListView, self).get_queryset()
                qs = qs.filter(is_deleted = False)

                auth_user = self.request.user
                partner_obj = Partner.objects.get(users=auth_user)
                qs = qs.filter(stockrecords__partner=partner_obj)
                if ProductClass.objects.filter(name='Combo'):
                    combo_class = ProductClass.objects.filter(name='Combo').last()
                    qs = qs.exclude(product_class=combo_class)
                return qs

        except:

            qs = super(FilteredProductListView, self).get_queryset()
            qs = qs.filter(stockrecords__id=0)

            return qs

    def apply_search(self, queryset):

        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('status'):

            queryset = queryset.filter(is_approved=data.get('status'))

        if data.get('category') and data.get('sub_category'):

            category_list = []

            category = Category.objects.filter(id=data.get('category').id)
            sub_category = Category.objects.filter(id=data.get('sub_category').id)

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            queryset = queryset.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = data.get('category')
            id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
            category = Category.objects.filter(id__in=id_list)
            queryset = queryset.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category').id)
            queryset = queryset.filter(categories__in=category.values_list('id', flat=True))

        if data.get('is_image'):

            product_with_image = ProductImage.objects.filter(product__id__in=queryset.values_list('id', flat=True))

            if data.get('is_image') == '1':     # Has image
                queryset = queryset.filter(id__in=product_with_image.values_list('product', flat=True))
            else:
                queryset = queryset.exclude(id__in=product_with_image.values_list('product', flat=True))

        if data.get('product_type'):

            product_class = None

            if data.get('product_type') == '1':     # Sale
                product_class = ProductClass.objects.filter(name='Sale')

            if data.get('product_type') == '2':     # Rent
                product_class = ProductClass.objects.filter(name='Rent')

            if data.get('product_type') == '3':     # Rent Or Sale
                product_class = ProductClass.objects.filter(name='Rent Or Sale')

            if data.get('product_type') == '4':     # Service
                product_class = ProductClass.objects.filter(name='Service')

            if data.get('product_type') == '5':     # Professional
                product_class = ProductClass.objects.filter(name='Professional')

            if product_class:
                queryset = queryset.filter(product_class=product_class.last())

        if data.get('upc'):

            matches_upc = Product.objects.filter(upc=data['upc'],is_deleted=False)
            qs_match = queryset.filter(Q(id__in=matches_upc.values('id')) | Q(id__in=matches_upc.values('parent_id')))

            if qs_match.exists():
                queryset = qs_match
            else:
                matches_upc = Product.objects.filter(upc__icontains=data['upc'],is_deleted=False)
                queryset = queryset.filter(Q(id__in=matches_upc.values('id')) | Q(id__in=matches_upc.values('parent_id')))

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

        return queryset


def export_rate_card_products(request):

    """
    Metho to export rate card
    :param request:
    :return: excel
    """

    try:

        data = request.GET

        qs_cost_product = ProductCostEntries.objects.filter(is_deleted=False).values_list('product', flat=True).distinct()
        qs = Product.objects.filter(id__in=qs_cost_product, product_cost_type='Multiple',is_deleted=False)

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            qs = qs.filter(id__in=checked_list)

        if data.get('product_upc'):
            qs = qs.filter(upc__icontains=data.get('product_upc'))

        if data.get('product'):
            qs = qs.filter(id=data.get('product'))

        if data.get('category') and data.get('sub_category'):

            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            qs = qs.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            qs = qs.filter(categories__in=id_list)

            # qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('transport_available'):

            transport_available = False

            if data.get('transport_available') == '1':
                transport_available = True

            qs = qs.filter(is_transporation_available=transport_available)

        excel_data = [
            [
                'Sr. No', 'Product Name', 'Product UPC', 'No of costs', 'Transport Available',
            ]
        ]

        counter = 0

        for data in qs:
            counter = counter + 1

            trs = 'No'
            if data.is_transporation_available:
                trs = 'Yes'

            excel_data.append(
                [
                    str(counter),
                    str(data.title), str(data.upc),
                    str(data.get_rate_card_count),
                    # str(data.product_cost_entries.all().count()),
                    trs
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'rate_card_product_costing_%s' % (str(datetime.datetime.now())),
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

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_rate_card_products_items(request):

    """
    Metho to export rate card
    :param request:
    :return: excel
    """

    try:

        data = request.GET

        pr_qs = Product.objects.filter(id=data.get('product_id'),is_deleted=False).last()

        qs = ProductCostEntries.objects.filter(product=pr_qs)
        if data.get('checked_id'):
            product_id = data.get('checked_id').split(',')
            qs = qs.filter(id__in=product_id)

        if data.get('product_upc'):
            qs = qs.filter(upc__icontains=data.get('product_upc'))

        if data.get('product'):
            qs = qs.filter(id=data.get('product'))

        if pr_qs.product_class.name == 'Rent Or Sale':

            qt_from, qt_to, req_day, cost_incl_tax, transport_incl_tax = \
                'Rent Quantity From', 'Rent Quantity To', 'Rent Requirement in Days', 'Rent Cost (Including TAX.)', \
                'Rent Transportation Cost (Including TAX.)'

            qt_from_sale, qt_to_sale, req_day_sale, cost_incl_tax_sale, transport_incl_tax_sale = \
                'Sale Quantity From', 'Sale Quantity To', 'Sale Requirement in Days', \
                'Sale Cost (Including TAX.)', \
                'Sale Transportation Cost (Including TAX.)'

            excel_data = [
                [
                    'Sr. No', 'Product Name', 'Product UPC',
                    qt_from, qt_to, req_day, cost_incl_tax, transport_incl_tax,
                    qt_from_sale, qt_to_sale, req_day_sale, cost_incl_tax_sale, transport_incl_tax_sale,
                ]
            ]

            counter = 0

            for data in qs:

                counter = counter + 1

                _qt_from, _qt_to, _req_day, _cost_incl_tax, _transport_incl_tax = '', '', '', '', ''
                _qt_from_sale, _qt_to_sale, _req_day_sale, _cost_incl_tax_sale, _transport_incl_tax_sale = '', '', '', '', ''

                _qt_from = data.rent_quantity_from
                _qt_to = data.rent_quantity_to
                _req_day = data.rent_requirement_day
                _cost_incl_tax = data.rent_cost_incl_tax
                _transport_incl_tax = data.rent_transport_cost

                _qt_from_sale = data.quantity_from
                _qt_to_sale = data.quantity_to
                _req_day_sale = data.requirement_day
                _cost_incl_tax_sale = data.cost_incl_tax
                _transport_incl_tax_sale = data.transport_cost

                excel_data.append(
                    [
                        str(counter),
                        str(data.product.title), str(data.product.upc),
                        _qt_from, _qt_to, _req_day, _cost_incl_tax,
                        _transport_incl_tax,
                        _qt_from_sale, _qt_to_sale, _req_day_sale, _cost_incl_tax_sale,
                        _transport_incl_tax_sale,

                    ]
                )

            prms = {
                'type': 'excel',
                'filename': 'rate_card_product_costing_%s' % (str(datetime.datetime.now())),
                'excel_data': excel_data
            }

            return utils.generate_excel(request, **prms)

        else:

            qt_from, qt_to, req_day, cost_incl_tax, transport_incl_tax = \
                    'Quantity From', 'Quantity To', 'Requirement in Days', 'Cost (Including TAX.)', \
                    'Transportation Cost (Including TAX.)'

            excel_data = [
                [
                    'Sr. No', 'Product Name', 'Product UPC',
                    qt_from, qt_to, req_day, cost_incl_tax, transport_incl_tax
                ]
            ]

            counter = 0

            for data in qs:

                counter = counter + 1

                _qt_from, _qt_to, _req_day, _cost_incl_tax, _transport_incl_tax = '', '', '', '', ''

                if pr_qs.product_class.name in ['Rent', 'Professional']:

                    _qt_from = data.rent_quantity_from
                    _qt_to = data.rent_quantity_to
                    _req_day = data.rent_requirement_day
                    _cost_incl_tax = data.rent_cost_incl_tax
                    _transport_incl_tax = data.rent_transport_cost

                if pr_qs.product_class.name in ['Sale']:
                    _qt_from = data.quantity_from
                    _qt_to = data.quantity_to
                    _req_day = data.requirement_day
                    _cost_incl_tax = data.cost_incl_tax
                    _transport_incl_tax = data.transport_cost

                excel_data.append(
                    [
                        str(counter),
                        str(data.product.title), str(data.product.upc),
                        _qt_from, _qt_to, _req_day, _cost_incl_tax,
                        _transport_incl_tax

                    ]
                )

            prms = {
                'type': 'excel',
                'filename': 'rate_card_product_costing_%s' % (str(datetime.datetime.now())),
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

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def get_event_products_rate_card(request):

    product_list = []

    try:

        if request.is_ajax():

            data = request.GET

            search = data.get('term[term]')

            entered_products = ProductCostEntries.objects.all().values_list('product__id', flat=True)

            products = Product.objects.filter(is_approved='Approved', product_cost_type='Multiple', is_deleted=False).exclude(id__in=entered_products)

            if not request.user.is_superuser:
                vendor = Partner.objects.filter(users=request.user)
                stock = StockRecord.objects.filter(partner=vendor.last())
                products = products.filter(id__in=stock.values_list('product', flat=True))

            products = products.filter(Q(upc__icontains=search) | Q(title__icontains=search))

            for product in products:
                product_dict = dict()
                product_dict['id'] = product.id
                product_dict['itemName'] = product.upc

                product_list.append(product_dict)

            return HttpResponse(json.dumps(product_list))

    except:

        return HttpResponse([])


@csrf_exempt
def delete_bulk_costing_product(request):

    """
    Ajax method to delete bulk product.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        product_id = request.GET.get('product_id')

        if not product_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        product_id_list = product_id.split(',')

        # check all ids are valid
        try:
            for obj in product_id_list:
                Product.objects.get(id=obj)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        prs = Product.objects.filter(id__in=product_id_list,is_deleted=False)
        ProductCostEntries.objects.filter(product__id__in=prs.values_list('id', flat=True)).delete()

        _pr_str = 'product'
        if len(product_id_list) > 1:
            _pr_str = 'products'

        success_str = 'Total %s %s deleted successfully.' % (len(product_id_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_costing_product_items(request):

    """
    Ajax method to delete bulk product.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        items = request.GET.get('items')

        if not items:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        items_list = items.split(',')

        # check all ids are valid
        try:
            for obj in items_list:
                ProductCostEntries.objects.get(id=obj)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        ProductCostEntries.objects.filter(id__in=items_list).delete()

        _pr_str = 'item'
        if len(items_list) > 1:
            _pr_str = 'items'

        success_str = 'Total %s %s deleted successfully.' % (len(items_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


class UpdateAdvancePayment(generic.View):

    def get(self, request, *args, **kwargs):

        sale_update_count, rent_update_count = 0, 0
        products = Product.objects.all()

        sale_product = products.filter(product_class__name='Sale')
        service_product = products.filter(product_class__name='Service')
        rent_pro = products.exclude(product_class__name__in=['Sale', 'Service'])

        for sp in sale_product:
            if StockRecord.objects.filter(product=sp):
                StockRecord.objects.filter(product=sp).update(advance_payment_percentage=100)
                sale_update_count = sale_update_count + 1

        for rp in rent_pro:
            if StockRecord.objects.filter(product=rp):
                StockRecord.objects.filter(product=rp).update(advance_payment_percentage=50)
                rent_update_count = rent_update_count + 1

        return HttpResponse(
            json.dumps(
                {
                    'total_product': products.count(),
                    'total_sale_product': sale_product.count(),
                    'total_rent_professional': rent_pro.count(),
                    'total_service_professional': service_product.count(),
                    'sale_update_count': sale_update_count,
                    'rent_update_count': rent_update_count,
                }
            )
        )


class FeaturedProductListView(generic.ListView):

    """
    Method to display featured product.
    """
    template_name = 'dashboard/featured_product/list.html'
    model = Product
    paginate_by = 20
    context_object_name = 'products'
    search_form = FeaturedProductSearchForm

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        return super(FeaturedProductListView, self).get(request, *args, **kwargs)

    def get_queryset(self):

        """
        Returns queryset
        :return: qs
        """

        data = self.request.GET

        qs = Product.objects.filter(is_featured_product = True, is_deleted = False)

        if data.get('product_upc'):
            qs = qs.filter(upc__icontains=data.get('product_upc'))
        #
        if data.get('category') and data.get('sub_category'):

            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            qs = qs.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            qs = qs.filter(categories__in=id_list)
            # qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('product'):
            qs = qs.filter(id=data.get('product'))


        return qs

    def get_context_data(self, **kwargs):

        """
        Return context data
        :param kwargs: dict
        :return: dict
        """

        ctx = super(FeaturedProductListView, self).get_context_data(**kwargs)

        ctx['form'] = self.search_form(data=self.request.GET)

        return ctx

@csrf_exempt
def get_products_for_featured(request):

    product_list = []

    try:

        if request.is_ajax():

            data = request.GET

            search = data.get('term[term]')

            products = Product.objects.filter(is_approved='Approved', is_deleted=False).exclude(is_featured_product =True)
            if not request.user.is_superuser:
                vendor = Partner.objects.filter(users=request.user)
                stock = StockRecord.objects.filter(partner=vendor.last())
                products = products.filter(id__in=stock.values_list('product', flat=True))

            products = products.filter(Q(upc__icontains=search) | Q(title__icontains=search))

            for product in products:
                product_dict = dict()
                product_dict['id'] = product.id
                product_dict['itemName'] = product.upc

                product_list.append(product_dict)

            return HttpResponse(json.dumps(product_list))

    except:

        return HttpResponse([])

@csrf_exempt
def add_product_featured(request):
    if request.is_ajax():

        items = request.GET.getlist('product[]')

        if not items:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Product.objects.filter(id__in = items).update(is_featured_product = True)

        _pr_str = 'product'
        if len(items) > 1:
            _pr_str = 'products'

        success_str = 'Added %s %s in featured product list.' % (len(items), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')

@csrf_exempt
def remove_featured_product(request):

    """
    Ajax method to delete bulk product.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        product_id = request.GET.get('product_id')

        if not product_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        product_id_list = product_id.split(',')

        # check all ids are valid
        try:
            for obj in product_id_list:
                Product.objects.get(id=obj)
        except:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        Product.objects.filter(id__in=product_id_list,is_deleted=False).update(is_featured_product = False)

        _pr_str = 'product'
        if len(product_id_list) > 1:
            _pr_str = 'products'

        success_str = 'Total %s %s remove successfully from featured product.' % (len(product_id_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


def export_featured_products(request):

    """
    Metho to export rate card
    :param request:
    :return: excel
    """

    try:

        data = request.GET

        qs = Product.objects.filter(is_featured_product = True, is_deleted=False)

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            qs = qs.filter(id__in=checked_list)

        if data.get('product_upc'):
            qs = qs.filter(upc__icontains=data.get('product_upc'))

        if data.get('product'):
            qs = qs.filter(id=data.get('product'))

        if data.get('category') and data.get('sub_category'):

            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            qs = qs.filter(categories__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            qs = qs.filter(categories__in=id_list)
            # qs = qs.filter(categories__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            qs = qs.filter(categories__in=category.values_list('id', flat=True))


        excel_data = [
            [
                'Sr. No', 'Product Name', 'Product UPC','Category Name'
            ]
        ]

        counter = 0

        for data in qs:
            counter = counter + 1

            excel_data.append(
                [
                    str(counter),
                    str(data.title), str(data.upc),
                    str(data.categories.all().last()),

                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'featured_product_costing_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except:

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

class RemoveFeaturedView(generic.View):

    """
    Method to delete rate card.
    """

    template_name = 'dashboard/featured_product/remove.html'

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context = dict()

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not Product.objects.filter(id=pk,is_deleted=False):
            return self.invalid_request('Select valid product.')

        product = Product.objects.get(id=pk)

        context['product'] = product

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not Product.objects.filter(id=pk,is_deleted=False):
            return self.invalid_request('Select valid product.')

        Product.objects.filter(id=pk).update(is_featured_product = False)
        messages.success(request, 'Remove product succesfully.')
        return HttpResponseRedirect(reverse('dashboard:featured-product-list'))


