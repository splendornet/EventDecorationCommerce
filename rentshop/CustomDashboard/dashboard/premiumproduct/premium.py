# python imports
import datetime

# django imports
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
from django.db.models import Q

# internal imports
from oscar.core.loading import get_class, get_model
from .premium_form import *
from CustomDashboard.dashboard import utils

Product = get_model('catalogue', 'Product')
PremiumProducts = get_model('catalogue', 'PremiumProducts')
StockRecord = get_model('partner', 'StockRecord')
Partner = get_model('partner', 'Partner')


class CreatePremiumProduct(generic.FormView):

    template_name = 'dashboard/premium/form.html'
    form_class = PremiumProductsModelForm

    success_url = reverse_lazy('dashboard:premium-index')

    def post(self, request, *args, **kwargs):
        existing_premium = None
        if not request.user.is_superuser:
            return self.invalid_request()

        premium_product = PremiumProducts.objects.filter(category=request.POST['category'])

        if premium_product:
            existing_premium = True
            form = self.form_class(request.POST, instance=premium_product.last())
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            if existing_premium:
                return self.is_valid(form, existing_premium)
            else:
                return self.is_valid(form, existing_premium)
        else:
            return self.is_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form, existing_premium):

        base_form = form.save(commit=False)

        base_form.save()
        form.save_m2m()
        if existing_premium:
            messages.success(self.request, 'Premium product updated successfully.')
        else:
            messages.success(self.request, 'Premium product created successfully.')
        return redirect('/dashboard/catalogue/premium/index/')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')


class PremiumProductDelete(generic.View):

    """
    Delete Premium product
    """

    template_name = 'dashboard/premium/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        premium_product = PremiumProducts.objects.filter(id=pk)

        if not premium_product:
            return self.invalid_request()

        context = dict()
        context['product'] = premium_product.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            premium_product = PremiumProducts.objects.filter(id=pk)

            if not premium_product:
                return self.invalid_request()

            PremiumProducts.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/catalogue/premium/index/')

        except:

            return self.invalid_request()


class PremiumProductUpdateView(generic.View):

    """
    To update premium product.
    """
    context_object_name = 'product'

    template_name = 'dashboard/premium/update_form.html'
    form_class = PremiumProductAddForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        premium_product = PremiumProducts.objects.filter(id=pk)

        if not premium_product:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=premium_product.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        premium_product = PremiumProducts.objects.filter(id=pk)

        if not premium_product:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=premium_product.last())

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form, premium_product)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/catalogue/premium/index/')

    def is_invalid(self, form, premium_product):

        context = dict()
        context['form'] = form
        context['category'] = premium_product.last().category.id
        return render(self.request, self.template_name, context=context)


class PremiumIndexView(generic.ListView):

    """
    premium product index page view.
    """

    template_name = 'dashboard/premium/index.html'
    model = PremiumProducts
    context_object_name = 'premium_product'
    paginate_by = 20
    form_class = PremiumSearchForm

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all().distinct('category')

            data = self.request.GET
            if data.get('category_title'):
                queryset = queryset.filter(category__name__icontains=data.get('category_title'))

            if data.get('category') and data.get('sub_category'):
                category_list = []

                category = Category.objects.filter(id=data.get('category'))
                sub_category = Category.objects.filter(id=data.get('sub_category'))

                category_list.extend(list(category.values_list('id', flat=True)))
                category_list.extend(list(sub_category.values_list('id', flat=True)))

                queryset = queryset.filter(category__id__in=category_list)

            if data.get('category') and not data.get('sub_category'):
                category = Category.objects.filter(id=data.get('category'))
                queryset = queryset.filter(category__id__in=category.values_list('id', flat=True))

            if data.get('sub_category') and not data.get('category'):
                category = Category.objects.filter(id=data.get('sub_category'))
                queryset = queryset.filter(category__id__in=category.values_list('id', flat=True))

            return queryset

        except Exception as e:
            print(e.args)

            return []

    def get_context_data(self, **kwargs):

        ctx = super(PremiumIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


def export_premium(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = PremiumProducts.objects.all().distinct('category')

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('category_title'):
            queryset = queryset.filter(category__name__icontains=data.get('category_title'))

        if data.get('category') and data.get('sub_category'):
            category_list = []

            category = Category.objects.filter(id=data.get('category'))
            sub_category = Category.objects.filter(id=data.get('sub_category'))

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            queryset = queryset.filter(category__id__in=category_list)

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category'))
            queryset = queryset.filter(category__id__in=category.values_list('id', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category'))
            queryset = queryset.filter(category__id__in=category.values_list('id', flat=True))

        excel_data = [
            [
                'Sr. No', 'Category', 'Products', 'Date Created'
            ]
        ]

        counter = 0

        for obj in queryset:
            ret = ''
            counter = counter + 1
            for product in obj.product.filter(is_deleted = False):
                ret = ret + product.title + ','
            excel_data.append(
                [
                    str(counter),
                    str(obj.category),
                    str(ret),
                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'premium_product_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_premium_data(request):

    """
    Ajax method to delete bulk premium.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        premium_id = request.GET.get('premium_id')
        if not premium_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        premium_list = premium_id.split(',')

        PremiumProducts.objects.filter(id__in=premium_list).delete()

        _pr_str = 'product'
        if len(premium_list) > 1:
            _pr_str = 'products'

        success_str = 'Total premium %s %s deleted successfully.' % (len(premium_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')


# Ajax Calls
def load_products(request):
    category_id = request.GET.get('category_id')
    prods = None
    if category_id:
        Category = get_model('catalogue', 'Category')

        cat = Category.objects.get(id=category_id)

        prods = cat.product_set.filter(is_approved='Approved', is_deleted=False)

    return render(request, 'admin/partials/product_dropdown_list_options.html', {'prods': prods})

# Ajax Calls
def load_products_byupc(request):
    upc_id = request.GET.get('upc_id')
    prods = None
    if upc_id:
        prods = Product.objects.filter(upc= upc_id,is_deleted=False)

    return render(request, 'admin/partials/product_dropdown_list_options.html', {'prods': prods})
