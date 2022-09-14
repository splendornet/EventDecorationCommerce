import math
import datetime

from django.shortcuts import HttpResponse, render, redirect, reverse
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy

# internal imports
from oscar.core.loading import get_class, get_model
from .cancellation_charge_form import *
from CustomDashboard.dashboard import utils
from django.views.generic import ListView

Product = get_model('catalogue', 'Product')
CancellationCharges = get_model('order', 'CancellationCharges')

class CancellationChargesIndexview(generic.ListView):
    template_name = 'dashboard/cancellation_charge/index.html'
    model = CancellationCharges
    context_obj_name = "canchrg"
    paginate_by = 15
    form_class = CancellationChargeSearchForm

    def get_queryset(self):
        try:
            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request,'Something went wrong')
                return redirect('/dashboard')
            queryset = self.model.objects.all()

            data = self.request.GET
            if data.get('charges_percentage'):
                queryset = queryset.filter(charges_percentage=data.get('charges_percentage'))

            if data.get('apply_to'):
                queryset = queryset.filter(apply_to=data.get('apply_to'))

            return queryset

        except Exception as e:
            print(e)

            return []

    def get_context_data(self, **kwargs):

        canchrg = super(CancellationChargesIndexview,self).get_context_data(**kwargs)
        canchrg['form'] = self.form_class(self.request.GET)

        return canchrg


class CreateCancellationCharge(generic.FormView):
    template_name = 'dashboard/cancellation_charge/form.html'
    template_name1 = 'dashboard/cancellation_charge/index.html'
    form_class = CancellationChargesModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs


    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        obj = CancellationCharges.objects.filter(apply_to = form.cleaned_data['apply_to'])
        if obj:
            CancellationCharges.objects.filter(apply_to = form.cleaned_data['apply_to']).update(
                charges_percentage=form.cleaned_data['charges_percentage'])
        else:
            CancellationCharges.objects.create(apply_to = form.cleaned_data['apply_to'],
                                              charges_percentage=form.cleaned_data['charges_percentage'])


        charges_percentage = form.cleaned_data['charges_percentage']
        apply_to = form.cleaned_data['apply_to']


        messages.success(self.request, 'Application charges created successfully.')
        return redirect('dashboard:cancellation_index')

    def invalid_request(self):
        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')


class DeleteCancellationCharge(generic.View):
    """

    """
    template_name = 'dashboard/cancellation_charge/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):
        print("----------------------")

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        cancellation_charges_obj = CancellationCharges.objects.filter(id=pk)

        if not cancellation_charges_obj:
            return self.invalid_request()

        context = dict()
        context['cancellation_charges'] = cancellation_charges_obj.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            cancellation_charges_obj = CancellationCharges.objects.filter(id=pk)

            if not cancellation_charges_obj:
                return self.invalid_request()

            CancellationCharges.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('dashboard:cancellation_index')


        except:

            return self.invalid_request()



class UpdateCancellationCharge(generic.View):
    """
    To update cancellation charge.
    """
    context_object_name = 'cancellation_charges'

    template_name = 'dashboard/cancellation_charge/update_form.html'
    form_class = CancellationChargesModelForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        cancellation_charges_obj = CancellationCharges.objects.filter(id=pk)

        if not cancellation_charges_obj:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=cancellation_charges_obj.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        cancellation_charges_obj = CancellationCharges.objects.filter(id=pk)

        if not cancellation_charges_obj:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=cancellation_charges_obj.last())

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        form.save()
        apply_to = form.cleaned_data['apply_to']
        charges_percentage = form.cleaned_data['charges_percentage']
        messages.success(self.request, 'Record updated successfully.')
        return redirect('dashboard:cancellation_index')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)


def export_cancellation_charges(request):
    try:

        data = request.GET


        queryset = CancellationCharges.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'cancellation_charges', 'Apply On', 'Products', 'Date Created'
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
                apply = 'Before 1 Month'
            elif obj.apply_to == '2':
                apply = 'Before 15 Days'
            elif obj.apply_to == '2':
                apply = 'Before 5 Days'
            else:
                apply = 'On the Event Date'
            excel_data.append(
                [
                    str(counter),
                    str(obj.charges_percentage),
                    apply,
                    str(ret),
                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'cancellationcharges_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

@csrf_exempt
def delete_bulk_cancellation_charges_data(request):

    """
    Ajax method to delete bulk premium.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        canchrg_id = request.GET.get('canchrg_id')
        if not canchrg_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        canchrg_list = canchrg_id.split(',')

        CancellationCharges.objects.filter(id__in=canchrg_list).delete()

        _pr_str = 'product'
        if len(canchrg_list) > 1:
            _pr_str = 'products'

        success_str = 'Total CancellationCharges %s %s deleted successfully.' % (len(canchrg_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')













