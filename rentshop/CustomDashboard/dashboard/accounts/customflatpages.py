# python imports
import datetime, json

# django imports
from django.db.models import Sum
from django.views.generic import TemplateView, View, ListView
from django.shortcuts import *
from django.contrib import messages
from django.db.models import Q
from django.views import generic
from django.urls import reverse, reverse_lazy


# packages imports
from oscar.core.loading import *
from oscar.apps.dashboard.views import IndexView
from oscar.core.compat import get_user_model

# internal imports
from .. import utils
from .flatpages_forms import *

CustomFlatPages = get_model('RentCore', 'CustomFlatPages')

User = get_user_model()


class CustomFlatPagesListView(ListView):

    template_name = 'dashboard/accounts/flatpages/list.html'
    form = CustomFlatPagesSearchForm
    model = CustomFlatPages
    paginate_by = 20
    context_object_name = 'products'

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form(self.request.GET)

        return ctx

    def get_queryset(self):

        qs = CustomFlatPages.objects.all()

        return qs


class CustomFlatPagesCreateUpateView(generic.FormView):

    """
    Flat pages view that can both create and update view.
    """

    template_name = 'dashboard/accounts/flatpages/form.html'

    form = CustomFlatPagesForm


    def get(self, request, *args, **kwargs):
        type = kwargs.get('type')
        form = self.form()
        if type == '1':
            cust_obj = CustomFlatPages.objects.filter(page_type = type)
            cust = cust_obj.last()
            form = self.form(instance=cust)
        return render(request, self.template_name,{'form': self.form})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)

        if request.user.is_superuser:
            addr = CustomFlatPages.objects.filter(page_type=type)

            if addr:
                form = self.form_class(request.POST, instance=addr.last())

        if form.is_valid():

            try:
                base_form = form.save(commit=False)

                base_form.save()

                return redirect('/dashboard/accounts/front-pages-index/')

            except Exception as e:

                messages.error(request, 'Something went wrong.')
                return redirect('/dashboard')

        else:
            pass

        return render(request, self.template_name, {'form': form})


class CustomFlatPagesCreateUpateViewV1(generic.FormView):

    """
    Combo view that can both create and update view.
    """

    template_name = 'dashboard/accounts/flatpages/form_v1.html'
    form = CustomFlatPagesCreateForm

    def get(self, request, *args, **kwargs):

        form = self.form()
        page_title, page_type = '', ''
        page_type = request.GET.get('type')

        if page_type not in ['0', '1', '2', '3','4','5']:
            messages.error(request, 'Invalid request.')
            return redirect('/dashboard')

        if page_type == '1':

            page_title = 'Policies'
            page_type = 1

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust)
            else:
                form = self.form()

        if page_type == '0':

            page_title = 'Legal Documents'
            page_type = 0

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust)
            else:
                form = self.form()

        if page_type == '2':

            page_title = 'Terms and Conditions'
            page_type = 2

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust)
            else:
                form = self.form()

        if page_type == '3':

            page_title = 'FAQ'
            page_type = 3

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust)
            else:
                form = self.form()

        if page_type == '4':

            page_title = 'About Us'
            page_type = 4

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust)
            else:
                form = self.form()

        if page_type == '5':

            page_title = 'How It Works'
            page_type = 5

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust)
            else:
                form = self.form()

        return render(request, self.template_name, {'form': form, 'page_title': page_title, 'page_type': page_type})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)

        if not form.is_valid():
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard')

        page_type = form.cleaned_data.get('page_type')

        if page_type == '0':

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust, data=request.POST)
                form.save()
                return self.success_url()
            else:
                form.save()
                return self.success_url()

        if page_type == '1':

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust, data=request.POST)
                form.save()
                return self.success_url()
            else:
                form.save()
                return self.success_url()

        if page_type == '2':

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust, data=request.POST)
                form.save()
                return self.success_url()
            else:
                form.save()
                return self.success_url()

        if page_type == '3':

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust, data=request.POST)
                form.save()
                return self.success_url()
            else:
                form.save()
                return self.success_url()

        if page_type == '4':

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust, data=request.POST)
                form.save()
                return self.success_url()
            else:
                form.save()
                return self.success_url()

        if page_type == '5':

            if CustomFlatPages.objects.filter(page_type=page_type):
                cust_obj = CustomFlatPages.objects.filter(page_type=page_type)
                cust = cust_obj.last()
                form = self.form(instance=cust, data=request.POST)
                form.save()
                return self.success_url()
            else:
                form.save()
                return self.success_url()


        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

    def success_url(self):

        messages.success(self.request, 'Record saved successfully.')
        return redirect('/dashboard/accounts/front-legal-page/')


class CustomFlatPagesCreateUpateView_V1(generic.FormView):
    """
    Combo view that can both create and update view.
    """

    template_name = 'dashboard/accounts/flatpages/create_update_form.html'

    form = CustomFlatPagesCreateForm

    def get(self, request, *args, **kwargs):
        data = self.request.GET
        type = data.get('type')

        if type :
            cust_obj = CustomFlatPages.objects.filter(page_type = type)
            cust = cust_obj.last()
            if cust:
                form = self.form(instance=cust)
            else:

                if type == '0':
                    form = self.form(initial={'url':"/legal/doc/",'title':"Legal Documents",'page_type':"0"})
                elif type =='1':
                    form = self.form(initial={'url':"/policies/",'title':"Policies",'page_type':"1"})
                elif type =='2':
                    form = self.form(initial={'url':"/terms-and-conditions/",'title':"Terms and Conditions",'page_type':"2"})

                else:
                    form= self.form

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)

        if request.user.is_superuser:

            addr = CustomFlatPages.objects.filter(page_type=type)

            if addr:
                form = self.form_class(request.POST, instance=addr.last())

        if form.is_valid():

            try:
                base_form = form.save(commit=False)

                base_form.save()

                return redirect('/dashboard/accounts/front-legal-page/')

            except Exception as e:

                messages.error(request, 'Something went wrong.')
                return redirect('/dashboard')

        else:
            pass

        return render(request, self.template_name, {'form': form})
