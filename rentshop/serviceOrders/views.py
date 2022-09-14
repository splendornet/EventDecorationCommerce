from datetime import timedelta, time
import json

from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, HttpResponse
from django.http import JsonResponse

from oscar.core.loading import get_model

from serviceOrders.forms import ServiceEnquiryForm
from serviceOrders.models import ServiceOrders
from serviceOrders.forms import ServiceOrderSearchForm
from CustomDashboard.dashboard import utils

Product = get_model('catalogue', 'Product')


class ServiceOrderView(TemplateView):

    def serviceEnquiry(request, productId):

        enquirySaved = False
        enquiryAlreadySent = False

        if request.method == 'POST':
            print(request.POST)
            form = ServiceEnquiryForm(request.POST)

            if form.is_valid():

                product = Product.objects.get(pk=productId)
                today = datetime.now().date()
                tomorrow = today + timedelta(1)
                today_start = datetime.combine(today, time())
                today_end = datetime.combine(tomorrow, time())

                data = request.POST

                # x_start_date = data.get('id_booking_start_date')
                # x_end_date = data.get('id_booking_end_date')
                print(data)
                x_booking_date = data.get('booking_date')

                # start_date = datetime.strptime(x_start_date, '%Y-%m-%d %I:%M %p')
                # end_date = datetime.strptime(x_end_date, '%Y-%m-%d %I:%M %p')
                booking_date = datetime.strptime(x_booking_date, '%Y-%m-%d')

                isAlreadyReg = ServiceOrders.objects.filter(product=product, added_date__lte=today_end, added_date__gte=today_start, mobile=request.POST['mobile_number'])
                if isAlreadyReg:

                    enquirySaved = False
                    enquiryAlreadySent = True
                    return render(request, 'serviceOrders/serviceEnqForm.html', {'form': form, 'enquirySaved': enquirySaved, 'productId': productId,'enquiryAlreadySent':enquiryAlreadySent})


                serviceEnqRegister = ServiceOrders.objects.create(mobile=request.POST['mobile_number'], product=product, name=request.POST['name'], email=request.POST['email'], booking_date=booking_date)

                enquirySaved = True
                messages.success(
                    request, 'Your response has been recorded successfully.'
                )

            else:
                return render(request, 'serviceOrders/serviceEnqForm.html',
                              {'form': form, 'enquirySaved': enquirySaved, 'productId': productId,'enquiryAlreadySent':enquiryAlreadySent})
        else:
            form = ServiceEnquiryForm()
        return render(request, 'serviceOrders/serviceEnquiry.html',{'form':form, 'enquirySaved':enquirySaved,'productId':productId,'enquiryAlreadySent':enquiryAlreadySent})


class ServiceOrderListView(generic.ListView):

    model = ServiceOrders
    context_object_name = 'serviceOrder'
    template_name = 'serviceOrders/serviceOrderList.html'
    form_class = ServiceOrderSearchForm
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE

    def get_queryset(self):
        qs = self.model._default_manager.all()
        self.description = _("All service orders")

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['name']:
            qs = qs.filter(name__icontains=data['name'])
            self.description = _("Partners matching '%s'") % data['name']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['queryset_description'] = self.description
        ctx['form'] = self.form
        ctx['is_filtered'] = self.is_filtered
        return ctx


def export_service_order(request):

    """
    Method to export units.
    """

    try:

        queryset = ServiceOrders.objects.all()

        data = request.GET

        if data.get('name'):
            queryset = queryset.filter(name__icontains=data.get('name'))

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'Product', 'Name', 'Email', 'Mobile', 'Enquiry Date'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(data.product), str(data.name),
                    str(data.email), str(data.mobile), str(data.added_date),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'service_order_enquiry_%s' % (str(datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


# Date: 18th Mar 2021
# View to add service product enquiry
def service_enquiry_ajax(request, productId):
    error = ''
    if request.method == 'POST':
        form = ServiceEnquiryForm(request.POST)
        if form.is_valid():

            product = Product.objects.get(pk=productId)

            data = request.POST

            x_booking_date = data.get('booking_date')
            booking_date = datetime.strptime(x_booking_date, '%Y-%m-%d')

            is_already_reg = ServiceOrders.objects.filter(product=product, booking_date=booking_date, mobile=request.POST.get('mobile_number'))
            message = 'Enquiry for the selected product and date is already registered'
            status = '2'
            if not is_already_reg:
                ServiceOrders.objects.create(mobile=request.POST.get('mobile_number'), product=product, name=request.POST.get('name'), email=request.POST.get('email'), booking_date=booking_date)
                message = 'Enquiry added successfully'
                status = '1'
        else:
            message = 'Invalid details'
            status = '0'
            error = json.loads(form.errors.as_json())
    else:
        message = 'Something went wrong'
        status = '10'
    result = {
        'message': message,
        'status': status,
        'error': error
    }
    return JsonResponse(result, safe=False)