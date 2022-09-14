# python imports
import datetime
import math

# django imports
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy

# internal imports
from oscar.core.loading import get_class, get_model
from .taxation_form import *
from CustomDashboard.dashboard import utils

Product = get_model('catalogue', 'Product')
Taxation = get_model('catalogue', 'Taxation')
updatetaxperc = get_class('RentCore.tasks', 'updatetaxperc')

class TaxationIndexView(generic.ListView):
    """
    taxation index page view.
    """

    template_name = 'dashboard/taxation/index.html'
    model = Taxation
    context_object_name = 'taxs'
    paginate_by = 20
    form_class = TaxationSearchForm

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all()
            data = self.request.GET

            if data.get('tax_percentage'):
                queryset = queryset.filter(tax_percentage=data.get('tax_percentage'))

            if data.get('apply_to'):
                queryset = queryset.filter(apply_to=data.get('apply_to'))

            return queryset

        except Exception as e:
            print(e.args)

            return []

    def get_context_data(self, **kwargs):

        ctx = super(TaxationIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class CreateTax(generic.FormView):
    template_name = 'dashboard/taxation/form.html'
    form_class = TaxationModelForm

    success_url = reverse_lazy('dashboard:taxation-index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        apply_to = form.cleaned_data['apply_to']

        tax_percentage = form.cleaned_data['tax_percentage']
        sale_tax = form.cleaned_data.get('sale_tax_percent')

        if apply_to == '1':

            product_obj = Product.objects.filter(product_class__name='Rent', is_deleted=False)
            if tax_percentage == 6:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                    price.rent_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.rent_round_off_price = diff
                    else:
                        price.rent_round_off_price = diff - 1
                    price.tax_percentage = tax_percentage

                    price.save()

        elif apply_to == '2':
            product_obj = Product.objects.filter(product_class__name='Sale', is_deleted=False)
            if tax_percentage == 1:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)

            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price_with_tax = (price.price_excl_tax * (tax_percentage / 100)) + price.price_excl_tax
                    price.sale_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.sale_round_off_price = diff
                    else:
                        price.sale_round_off_price = diff - 1
                    price.tax_percentage = tax_percentage
                    price.save()

        elif apply_to == '3':
            product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)
            if tax_percentage == 6 and sale_tax == 1:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18 and sale_tax == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)

            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    # Save Sale Price
                    price_with_tax = (price.price_excl_tax * (sale_tax / 100)) + price.price_excl_tax
                    price.sale_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.sale_round_off_price = diff
                    else:
                        price.sale_round_off_price = diff - 1
                    price.sale_tax_percentage = sale_tax
                    price.save()

                    # Save Rent Price
                    price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                    price.rent_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.rent_round_off_price = diff
                    else:
                        price.rent_round_off_price = diff - 1
                    price.tax_percentage = tax_percentage

                    price.save()

        elif apply_to == '4':

            product_obj = Product.objects.filter(product_class__name='Professional', is_deleted=False)
            if tax_percentage == 6 and sale_tax == 1:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18 and sale_tax == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                    price.rent_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.rent_round_off_price = diff
                    else:
                        price.rent_round_off_price = diff - 1

                    price.tax_percentage = tax_percentage
                    price.save()

        else:
            products = form.cleaned_data['products']
            product_obj = Product.objects.filter(id__in=products, is_deleted=False)
            #
            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    if product.product_class.name == 'Rent' or 'Rent or Sale' or 'Professional':
                        price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                        price.rent_price_with_tax = price_with_tax
                        ceil_price = math.ceil(price_with_tax)
                        diff = ceil_price - price_with_tax
                        if diff <= 0.50:
                            price.rent_round_off_price = diff
                        else:
                            price.rent_round_off_price = diff - 1
                        price.tax_percentage = tax_percentage

                        price.save()

                    elif product.product_class.name == 'Sale' or 'Rent or Sale':
                        price_with_tax = (price.price_excl_tax * (tax_percentage / 100)) + price.price_excl_tax
                        price.sale_price_with_tax = price_with_tax
                        ceil_price = math.ceil(price_with_tax)
                        diff = ceil_price - price_with_tax
                        if diff <= 0.50:
                            price.sale_round_off_price = diff
                        else:
                            price.sale_round_off_price = diff - 1
                        price.tax_percentage = tax_percentage

                        price.save()

        messages.success(self.request, 'Tax created successfully.')
        return redirect('/dashboard/catalogue/taxation/index/')

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')


class TaxDelete(generic.View):
    """

    """

    template_name = 'dashboard/taxation/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        tax_obj = Taxation.objects.filter(id=pk)

        if not tax_obj:
            return self.invalid_request()

        context = dict()
        context['tax'] = tax_obj.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            tax_obj = Taxation.objects.filter(id=pk)

            if not tax_obj:
                return self.invalid_request()

            Taxation.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/catalogue/taxation/index/')

        except:

            return self.invalid_request()


class TaxUpdateView(generic.View):
    """
    To update premium product.
    """
    context_object_name = 'tax'

    template_name = 'dashboard/taxation/form.html'
    form_class = TaxationModelForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        tax_obj = Taxation.objects.filter(id=pk)

        if not tax_obj:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=tax_obj.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        tax_obj = Taxation.objects.filter(id=pk)

        if not tax_obj:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=tax_obj.last())

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        apply_to = form.cleaned_data['apply_to']

        tax_percentage = form.cleaned_data['tax_percentage']
        sale_tax = form.cleaned_data.get('sale_tax_percent')

        if apply_to == '1':

            product_obj = Product.objects.filter(product_class__name='Rent', is_deleted=False)
            if tax_percentage == 6:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                    price.rent_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.rent_round_off_price = diff
                    else:
                        price.rent_round_off_price = diff - 1

                    price.tax_percentage = tax_percentage
                    price.save()

        elif apply_to == '4':

            product_obj = Product.objects.filter(product_class__name='Professional', is_deleted=False)
            if tax_percentage == 6:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)
            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                    price.rent_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.rent_round_off_price = diff
                    else:
                        price.rent_round_off_price = diff - 1

                    price.tax_percentage = tax_percentage
                    price.save()

        elif apply_to == '2':
            product_obj = Product.objects.filter(product_class__name='Sale', is_deleted=False)
            if tax_percentage == 6:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)
            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    price_with_tax = (price.price_excl_tax * (tax_percentage / 100)) + price.price_excl_tax
                    price.sale_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.sale_round_off_price = diff
                    else:
                        price.sale_round_off_price = diff - 1
                    price.tax_percentage = tax_percentage

                    price.save()

        elif apply_to == '3':
            product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)
            if tax_percentage == 6 and sale_tax == 1:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18 and sale_tax == 18:
                product_tax_type = 'regular_tax'
            else:
                messages.error(self.request, 'Please enter valid tax percentage')
                return render(self.request, self.template_name, context={'form': form})
            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)
            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    # Save Sale Price
                    price_with_tax = (price.price_excl_tax * (sale_tax / 100)) + price.price_excl_tax
                    price.sale_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.sale_round_off_price = diff
                    else:
                        price.sale_round_off_price = diff - 1
                    price.sale_tax_percentage = sale_tax
                    price.save()

                    # Save Rent Price
                    price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                    price.rent_price_with_tax = price_with_tax
                    ceil_price = math.ceil(price_with_tax)
                    diff = ceil_price - price_with_tax
                    if diff <= 0.50:
                        price.rent_round_off_price = diff
                    else:
                        price.rent_round_off_price = diff - 1
                    price.tax_percentage = tax_percentage

                    price.save()

        else:

            products = form.cleaned_data['products']

            product_obj = Product.objects.filter(id__in=products, is_deleted=False)
            #
            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:

                    if product.product_class.name == 'Rent' or 'Rent or Sale' or 'Professional':
                        price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price

                        price.rent_price_with_tax = price_with_tax
                        ceil_price = math.ceil(price_with_tax)
                        diff = ceil_price - price_with_tax
                        if diff <= 0.50:
                            price.rent_round_off_price = diff
                        else:
                            price.rent_round_off_price = diff - 1
                        price.tax_percentage = tax_percentage

                        price.save()

                    elif product.product_class.name == 'Sale' or 'Rent or Sale':

                        price_with_tax = (price.price_excl_tax * (tax_percentage / 100)) + price.price_excl_tax
                        price.sale_price_with_tax = price_with_tax
                        ceil_price = math.ceil(price_with_tax)
                        diff = ceil_price - price_with_tax
                        if diff <= 0.50:
                            price.sale_round_off_price = diff
                        else:
                            price.sale_round_off_price = diff - 1

                        price.tax_percentage = tax_percentage
                        price.save()

        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/catalogue/taxation/index/')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)


def export_tax(request):
    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = Taxation.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'Tax', 'Apply On', 'Products', 'Date Created'
            ]
        ]

        counter = 0

        for obj in queryset:
            ret = ''
            counter = counter + 1
            apply = ' '
            for product in obj.products.all():
                ret = ret + product.title + ','
            if obj.apply_to == '1':
                apply = 'For all rental products'
            elif obj.apply_to == '2':
                apply = 'For all selling products'
            elif obj.apply_to == '3':
                apply = 'For all rent and sale products'
            else:
                apply = 'For all professional products'
            excel_data.append(
                [
                    str(counter),
                    str(obj.tax_percentage),
                    apply,
                    str(ret),
                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'tax_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_tax_data(request):
    """
    Ajax method to delete bulk premium.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        tax_id = request.GET.get('tax_id')
        if not tax_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        tax_list = tax_id.split(',')

        Taxation.objects.filter(id__in=tax_list).delete()

        _pr_str = 'taxation'
        if len(tax_list) > 1:
            _pr_str = 'taxations'

        success_str = 'Total %s %s deleted successfully.' % (len(tax_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')

class CreateUpdateTaxPercentageView(generic.FormView):
    """
    tax view that can both create and update view.
    """

    template_name = 'dashboard/taxation/form.html'
    form = TaxationModelForm

    success_url = reverse_lazy('dashboard:taxation-index')
    def get(self, request, *args, **kwargs):
        data = self.request.GET
        type = data.get('type')

        if type :
            cust_obj = Taxation.objects.filter(apply_to = type)
            cust = cust_obj.last()
            if cust:
                form = self.form(instance=cust)
            else:
                if type:
                    form = self.form(initial={'apply_to':type})
                else:
                    form= self.form

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)
        if not form.is_valid():
            self.form_invalid(form)

        apply_to = request.GET.get('type')
        tax_percentage = form.cleaned_data['tax_percentage']
        sale_tax = form.cleaned_data['sale_tax_percent']
        apply_to = int(apply_to)
        if apply_to == 1:
            if not tax_percentage == 6 and not tax_percentage ==18:
                messages.error(self.request, 'Please enter valid tax percentage')
                form= self.form(initial={'apply_to': apply_to,'tax_percentage':tax_percentage})
                return render(self.request, self.template_name, context={'form': form})
        if apply_to == 2:
            if not tax_percentage == 1 and not tax_percentage ==18:
                messages.error(self.request, 'Please enter valid tax percentage')
                form= self.form(initial={'apply_to': apply_to,'tax_percentage':tax_percentage})
                return render(self.request, self.template_name, context={'form': form})
        else:
            if not (tax_percentage == 6 and sale_tax == 1) and not(tax_percentage == 18 and sale_tax == 18):
                messages.error(self.request, 'Please enter valid tax percentage')
                form= self.form(initial={'apply_to': apply_to,'tax_percentage':tax_percentage,'sale_tax_percent':sale_tax})
                return render(self.request, self.template_name, context={'form': form})

        if apply_to:
            tax_obj = Taxation.objects.filter(apply_to=apply_to)

            if tax_obj:
                tax = tax_obj.last()
                tax.tax_percentage = tax_percentage
                tax.sale_tax_percent = sale_tax
                tax.save()
            else:
                base_form = form.save(commit=False)
                base_form.apply_to = request.GET.get('type')
                base_form.save()

            data = {
                'tax_percentage': tax_percentage,
                'sale_tax':sale_tax,
                'apply_to': apply_to
            }
            updatetaxperc.delay(**data)
            return self.success_url()

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

    def success_url(self):

        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/catalogue/taxation/index/')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)




