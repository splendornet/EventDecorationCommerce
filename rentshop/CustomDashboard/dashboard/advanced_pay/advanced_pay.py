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
from .advanced_pay_form import *

from CustomDashboard.dashboard import utils


Product = get_model('catalogue', 'Product')
AdvancedPayPercentage = get_model('catalogue', 'AdvancedPayPercentage')
updateadvpayperc = get_class('RentCore.tasks', 'updateadvpayperc')


class PercentageIndexView(generic.ListView):

    """
    advanced payment percentage index page view.
    """

    template_name = 'dashboard/advanced_pay/index.html'
    model = AdvancedPayPercentage
    context_object_name = 'taxs'
    paginate_by = 20
    form_class = PercentageSearchForm

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all()
            data = self.request.GET

            if data.get('advance_payment_percentage'):
                queryset = queryset.filter(advance_payment_percentage=data.get('advance_payment_percentage'))

            if data.get('apply_to'):
                queryset = queryset.filter(apply_to=data.get('apply_to'))

            return queryset

        except Exception as e:
            print(e.args)

            return []

    def get_context_data(self, **kwargs):

        ctx = super(PercentageIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class CreatePercentage(generic.FormView):

    template_name = 'dashboard/advanced_pay/form.html'
    form_class = PercentageModelForm

    success_url = reverse_lazy('dashboard:adv-percentage-index')

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
        apply_to = form.cleaned_data['apply_to']

        advance_payment_percentage = form.cleaned_data['advance_payment_percentage']

        data = {
            'advance_payment_percentage' : advance_payment_percentage,
            'apply_to': apply_to
        }
        updateadvpayperc(**data)



        # if apply_to == '1':
        #
        #     product_obj = Product.objects.filter(product_class__name='Rent', is_deleted=False)
        #
        #     for product in product_obj:
        #         price_obj = product.stockrecords.all()
        #         price = price_obj.last()
        #         if price:
        #             price.advance_payment_percentage = advance_payment_percentage
        #             price.save()
        #
        # elif apply_to == '2':
        #     product_obj = Product.objects.filter(product_class__name='Sale', is_deleted=False)
        #
        #     for product in product_obj:
        #
        #         price_obj = product.stockrecords.all()
        #         price = price_obj.last()
        #         if price:
        #             price.advance_payment_percentage = advance_payment_percentage
        #             price.save()
        #
        # elif apply_to == '3':
        #     product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)
        #
        #     for product in product_obj:
        #
        #         price_obj = product.stockrecords.all()
        #         price = price_obj.last()
        #         if price:
        #             price.advance_payment_percentage = advance_payment_percentage
        #             price.save()
        #
        # elif apply_to == '4':
        #
        #     product_obj = Product.objects.filter(product_class__name='Professional', is_deleted=False)
        #
        #     for product in product_obj:
        #         price_obj = product.stockrecords.all()
        #         price = price_obj.last()
        #         if price:
        #             price.advance_payment_percentage = advance_payment_percentage
        #             price.save()

        messages.success(self.request, 'advance payment percentage created successfully.')
        return redirect('/dashboard/catalogue/adv_percentage/index/')

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')


class PercentageDelete(generic.View):

    """
    advanced payment percentage delete view
    """

    template_name = 'dashboard/advanced_pay/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        tax_obj = AdvancedPayPercentage.objects.filter(id=pk)

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

            tax_obj = AdvancedPayPercentage.objects.filter(id=pk)

            if not tax_obj:
                return self.invalid_request()

            AdvancedPayPercentage.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/catalogue/adv_percentage/index/')

        except:

            return self.invalid_request()


class PercentageUpdateView(generic.View):

    """
    To update  percentage.
    """
    context_object_name = 'tax'

    template_name = 'dashboard/advanced_pay/form.html'
    form_class = PercentageModelForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        tax_obj = AdvancedPayPercentage.objects.filter(id=pk)

        if not tax_obj:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=tax_obj.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        tax_obj = AdvancedPayPercentage.objects.filter(id=pk)

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
        apply_to = form.cleaned_data['apply_to']

        advance_payment_percentage = form.cleaned_data['advance_payment_percentage']

        if apply_to == '1':

            product_obj = Product.objects.filter(product_class__name='Rent',is_deleted=False)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage
                    price.save()

        elif apply_to == '4':

            product_obj = Product.objects.filter(product_class__name='Professional',is_deleted=False)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage
                    price.save()

        elif apply_to == '2':
            product_obj = Product.objects.filter(product_class__name='Sale',is_deleted=False)

            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage

                    price.save()

        elif apply_to == '3':
            product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)

            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage
                    price.save()

        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/catalogue/adv_percentage/index/')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)


def export_percentage(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = AdvancedPayPercentage.objects.all()

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'Advanced Payment Percentage','Apply On', 'Date Created'
            ]
        ]

        counter = 0

        for obj in queryset:
            ret = ''
            counter = counter + 1
            apply = ' '
            # for product in obj.products.all():
            #     ret = ret + product.title + ','
            if obj.apply_to == '1':
                apply =  'For all rental products'
            elif obj.apply_to == '2':
                apply = 'For all selling products'
            elif obj.apply_to == '3' :
                apply = 'For all rent and sale products'
            else:
                apply = 'For professional products'
            excel_data.append(
                [
                    str(counter),
                    str(obj.advance_payment_percentage),
                    apply,

                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'advanced_payment_percentage_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_percentage_data(request):

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

        AdvancedPayPercentage.objects.filter(id__in=tax_list).delete()

        _pr_str = 'percentage'
        if len(tax_list) > 1:
            _pr_str = 'percentages'

        success_str = 'Total %s advanced payment %s deleted successfully.' % (len(tax_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')



class CreateUpdatePercentageView(generic.FormView):
    """
    Combo view that can both create and update view.
    """

    template_name = 'dashboard/advanced_pay/form.html'

    form = PercentageModelForm

    def get(self, request, *args, **kwargs):
        data = self.request.GET
        type = data.get('type')

        if type :
            cust_obj = AdvancedPayPercentage.objects.filter(apply_to = type)
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
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard')

        apply_to = request.GET.get('type')
        apply_to = int(apply_to)
        if apply_to:
            cust_obj = AdvancedPayPercentage.objects.filter(apply_to=apply_to)
            advance_payment_percentage = form.cleaned_data['advance_payment_percentage']
            sale_advance_payment_percentage = form.cleaned_data['sale_advance_payment_percentage']
            if cust_obj:
                cust = cust_obj.last()
                cust.advance_payment_percentage = advance_payment_percentage
                cust.sale_advance_payment_percentage = sale_advance_payment_percentage
                cust.save()

            else:
                base_form = form.save(commit=False)
                base_form.apply_to = request.GET.get('type')
                base_form.save()

            data = {
                'advance_payment_percentage': advance_payment_percentage,
                'sale_advance_payment_percentage': sale_advance_payment_percentage,
                'apply_to': apply_to
            }
            updateadvpayperc.delay(**data)

        return self.success_url()

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

    def success_url(self):

        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/catalogue/adv_percentage/index/')

