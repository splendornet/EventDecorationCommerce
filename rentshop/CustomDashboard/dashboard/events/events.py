# python import
import json

# django imports
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse, render, redirect
from django.db.models import Q
from django.urls import reverse
from django.views.generic import View
from django.contrib import messages

# packages import
from oscar.core.loading import get_classes, get_model

# internal imports
from .events_forms import *

Product = get_model('catalogue', 'Product')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')


@csrf_exempt
def get_event_products(request):

    product_list = []

    try:

        if request.is_ajax():

            data = request.GET

            search = data.get('term[term]')

            products = Product.objects.filter(is_approved='Approved', is_deleted=False)

            if not request.user.is_superuser:
                vendor = Partner.objects.filter(users=request.user)
                stock = StockRecord.objects.filter(partner=vendor.last())
                products = products.filter(id__in=stock.values_list('product', flat=True))

            if request.user.is_superuser:
                vendor = Partner.objects.filter(id=data.get('vendor'))
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


class CreateEventAdmin(View):

    template_name = 'dashboard/events/form.html'
    form_class = AdminCalendarAddEvent

    def invaid_request(self, message):

        messages.error(self.request, message)
        return redirect(reverse('dashboard:home'))

    def get(self, request, *args, **kwargs):

        context = dict()
        context['form'] = self.form_class

        user = request.user

        if not user.is_active or not user.is_superuser:
            return self.invaid_request('Invalid request.')

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        if not form.is_valid():
            messages.error(request, 'Please correct below errors.')
            return render(self.request, self.template_name, {'form': form})

        base_form = form.save(commit=False)
        base_form.save()

        messages.success(self.request, 'Event added successfully.')
        return redirect('dashboard:vendor-calender')


class UpdateEventAdmin(View):

    template_name = 'dashboard/events/form.html'
    form_class = AdminCalendarAddEvent

    def invaid_request(self, message):

        messages.error(self.request, message)
        return redirect(reverse('dashboard:home'))

    def get(self, request, *args, **kwargs):

        context = dict()

        user = request.user
        pk = kwargs.get('pk')

        if not pk or not VendorCalender.objects.filter(id=pk):
            return self.invaid_request('Invalid event.')

        instance = VendorCalender.objects.get(id=pk)
        context['form'] = self.form_class(instance=instance)

        if not user.is_active or not user.is_superuser:
            return self.invaid_request('Invalid request.')

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')
            instance = VendorCalender.objects.get(id=pk)
            form = self.form_class(request.POST, instance=instance)

            if not form.is_valid():
                messages.error(request, 'Please correct below errors.')
                return render(self.request, self.template_name, {'form': form})

            base_form = form.save(commit=False)
            base_form.save()

            messages.success(self.request, 'Event added successfully.')
            return redirect('dashboard:vendor-calender')

        except:

            return self.invaid_request('Something went wrong.')
