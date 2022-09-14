# python imports
import datetime, json

# django imports
from django.shortcuts import HttpResponse, render, redirect
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
from CustomDashboard.dashboard import utils


# packages imports
from oscar.core.loading import get_class, get_model

# internal import
from .best_quote_form import *


Enquiry = get_model('customer', 'Enquiry')
Partner = get_model('partner', 'Partner')

generate_excel = get_class('dashboard.utils', 'generate_excel')


class BestQuoteView(generic.ListView):

    """
    best quote index page view.
    """

    template_name = 'dashboard/sales/best_quote/index.html'
    model = Enquiry
    context_object_name = 'quote'
    paginate_by = 20
    form_class = EnquirySearchForm

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all().order_by('-id')

            data = self.request.GET

            if data.get('organization_name'):
                queryset = queryset.filter(organization_name__icontains=data.get('organization_name'))

            if data.get('person_name'):
                queryset = queryset.filter(person_name__icontains=data.get('person_name'))

            if data.get('email'):
                queryset = queryset.filter(email__icontains=data.get('email'))

            if data.get('city'):
                queryset = queryset.filter(city__icontains=data.get('city'))

            return queryset

        except Exception as e:

            return []

    def get_context_data(self, **kwargs):

        ctx = super(BestQuoteView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class BestQuoteAllocateView(generic.View):

    template_name = 'dashboard/sales/best_quote/details.html'

    form = OrderAllocateForm

    def invalid_request(self, message):
        messages.error(self.request, message)
        return redirect(reverse('dashboard:index'))

    def get(self, request, *args, **kwargs):

        user = request.user
        quote_id = self.kwargs.get('pk')

        # validate user
        if not user.is_active or not user.is_superuser:
            return self.invalid_request('Invalid request.')

        # validate order
        if not quote_id or not Enquiry.objects.filter(id=quote_id):
            return self.invalid_request('Invalid quote.')

        quote = Enquiry.objects.get(id=quote_id)

        context = dict()
        context['quote'] = quote
        context['form'] = self.form(self.request.GET)

        return render(self.request, self.template_name, context=context)

    def post(self,request,*args,**kwargs):

        form = self.form(request.POST)
        quote_id = self.kwargs.get('pk')

        if form.is_valid():

            try:
                obj = Enquiry.objects.filter(id=quote_id)
                vend = form.cleaned_data.get('vendors',False)

                obj.last().allocated_vendor.add(*vend)
                messages.success(request, 'Allocated to ASP. Please generate order now.')
                return redirect('/dashboard/partners/best_quote/best_quote_allocate/'+str(quote_id)+'/')

            except Exception as e:

                messages.error(request, 'Something went wrong.')
                return redirect('/dashboard/')

        return redirect('/dashboard/')


def allocate_vendor_best_quote(request):

    try:

        data = request.POST

        vendors = data.getlist('vendors')

        return HttpResponse('200')

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return HttpResponse('IN_SERVER')



@csrf_exempt
def get_vendors_best_quote(request):

    vendor_list = []
    try:

        if request.is_ajax():

            data = request.GET

            vendors = Partner.objects.all().values_list('product__id', flat=True)

            vendors = Partner.objects.filter(is_approved='Approved')

            if not request.user.is_superuser:
                vendors = Partner.objects.all()


            for vendor in vendors:
                vendor_dict = dict()
                vendor_dict['id'] = vendor.id
                vendor_dict['name'] = vendor.name

                vendor_list.append(vendor_dict)
            return HttpResponse(json.dumps(vendor_list))

    except:

        return HttpResponse([])


@csrf_exempt
def delete_bulk_quote_data(request):

    """
    Ajax method to delete bulk best quote.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        quote_id = request.GET.get('quote_id')
        if not quote_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        quote_list = quote_id.split(',')

        Enquiry.objects.filter(id__in=quote_list).delete()

        _pr_str = 'quote'
        if len(quote_list) > 1:
            _pr_str = 'quotes'

        success_str = 'Total  %s  best %s deleted successfully.' % (len(quote_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')

class BestQuoteDelete(generic.View):

    """
    delete best quote
    """

    template_name = 'dashboard/sales/best_quote/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        enquiry_obj = Enquiry.objects.filter(id=pk)

        if not enquiry_obj:
            return self.invalid_request()

        context = dict()
        context['product'] = enquiry_obj.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            enquiry_obj = Enquiry.objects.filter(id=pk)

            if not enquiry_obj:
                return self.invalid_request()

            Enquiry.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/partners/best_quote')

        except:

            return self.invalid_request()


def export_quote(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = Enquiry.objects.all()

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('organization_name'):
            queryset = queryset.filter(organization_name__icontains=data.get('organization_name'))

        if data.get('person_name'):
            queryset = queryset.filter(person_name__icontains=data.get('person_name'))

        if data.get('email'):
            queryset = queryset.filter(email__icontains=data.get('email'))

        if data.get('city'):
            queryset = queryset.filter(city__icontains=data.get('city'))

        # if data.get('category_title'):
        #     queryset = queryset.filter(category__name__icontains=data.get('category_title'))
        '', '',
        'email', 'enquiry_text',
        'rental_duration', 'budget_from', 'city', 'budget_to',

        excel_data = [
            [
                'Sr. No','Person Name',  'Organization Name', 'Telephone Number','Email','Event Date''Date Created'
            ]
        ]

        counter = 0

        for obj in queryset:
            ret = ''
            counter = counter + 1
            excel_data.append(
                [
                    str(counter),
                    str(obj.person_name),
                    str(obj.organization_name),
                    str(obj.telephone_number),
                    str(obj.email),
                    str(obj.event_date.date()),
                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'quote_product_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')
