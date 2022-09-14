# python imports
import json
import random
import string
import csv
import tablib
from itertools import chain
from import_export import resources

# django imports
from django.contrib.auth.models import Group
from django.views.generic import TemplateView, ListView, View
from django.contrib.sites.models import Site
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView, ListView, View
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from oscar.core.loading import get_class, get_model

# 3rd party imports
from CustomPartner.partner.models import Partner

# internal imports
from .resources import account_activation_token
from .forms import *
from country.models import State, City


Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
send_email = get_class('RentCore.email', 'send_email')
check_cron = get_class('RentCore.tasks', 'check_cron')
send_sms = get_class('RentCore.email', 'send_sms')


class IndexPartner(TemplateView):

    """
    Partner index view.
    """

    template_name = 'partner/index.html'


class AddPartner(View):

    """
    Vendor register form
    """

    form_class_partner = PartnerForm
    form_user_class = User_Form
    initial = {'a':'b'}
    # template_name = 'partner/cafe.html'
    template_name = 'new_design/partner/cafe.html'
    #
    def get(self, request, *args, **kwargs):
        print('in get')

        form = self.form_class_partner(initial=self.initial)
        form_user = self.form_user_class(initial=self.initial)

        return render(request, self.template_name, {'form': form,'form_user': form_user})

    def post(self, request, *args, **kwargs):
        print('in post')
        form_partner_obj = self.form_class_partner(request.POST, request.FILES)
        form_user_obj = self.form_user_class(request.POST)
        print('in valid',form_partner_obj.is_valid(),form_user_obj.is_valid())
        print('in valid',form_partner_obj,form_user_obj)
        if form_partner_obj.is_valid() and form_user_obj.is_valid():

            try:

                fullname = form_partner_obj.cleaned_data['name'].lower()
                fTup = fullname.partition(' ')
                user_obj = form_user_obj.save(commit=False)

                user_obj.username = user_obj.email
                user_obj.email = user_obj.email
                user_obj.first_name = fTup[0]
                user_obj.last_name = fTup[2]

                # set password
                pwd_length = 8
                pwd = (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(pwd_length)))
                user_obj.set_password(pwd),
                user_obj.is_staff = True
                user_obj.is_active = False

                # save partner form
                partner_obj = form_partner_obj.save(commit=False)
                partner_obj.name = form_partner_obj.cleaned_data['name']
                partner_obj.telephone_number = form_partner_obj.cleaned_data['telephone_number']
                partner_obj.alternate_mobile_number = form_partner_obj.cleaned_data['alternate_mobile_number']
                partner_obj.address_line_1 = form_partner_obj.cleaned_data['address_line_1']
                partner_obj.address_line_2 = form_partner_obj.cleaned_data['address_line_2']
                partner_obj.country = form_partner_obj.cleaned_data['country']
                partner_obj.state = form_partner_obj.cleaned_data['state']
                partner_obj.city = form_partner_obj.cleaned_data['city']

                partner_obj.pincode = form_partner_obj.cleaned_data['pincode']
                partner_obj.categories = form_partner_obj.cleaned_data['categories']
                partner_obj.business_name = form_partner_obj.cleaned_data['business_name']
                partner_obj.email_id = user_obj.email

                user_obj.save()
                partner_obj.save()

                partner_obj.users.add(user_obj.id)
                Group.objects.get(name='Vendor').user_set.add(user_obj)
                current_site = Site.objects.get_current()

                # Vendor register email function
                # mail_subject = 'Congratulations and welcome in our family.'
                mail_subject = 'TakeRentPe - Account Login Credential Email.'
                message = render_to_string('customer/emails/email_password_email.html', {'vendor': user_obj,'email_id':user_obj.email,'pwd':pwd, 'domain': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(), 'token': account_activation_token.make_token(user_obj),})
                to_email = user_obj.email
                from_email = settings.FROM_EMAIL_ADDRESS
                email = EmailMessage(mail_subject, message, from_email, [to_email])
                email.content_subtype = "html"
                email.send()

                vendor_welcome_email_data = {
                    # 'mail_subject': 'TakeRentPe - Congratulations and welcome in our family.',
                    'mail_subject': 'TakeRentPe - Account Login Credential Email.',
                    'mail_template': 'customer/emails/email_password_email.html',
                    'mail_type' :'account_login_credential_email',
                    'mail_to': [user_obj.email],
                    'mail_context': {
                        'vendor': user_obj, 'email_id':user_obj.email,
                        'pwd':pwd, 'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(),
                        'token': account_activation_token.make_token(user_obj),
                    }
                }
                send_email(**vendor_welcome_email_data)

                # sms send code ASP ACCOUNT LOG IN CREDENTIAL SMS
                message = 'DASHBOARD ACCESS \nEmail: '+str(user_obj.email)+'\nPassword: ' + str(pwd) + '\nIf you have any questions, please let us know. We will respond you ASAP! Happy celebranto!'
                msg_kwargs = {
                    'message': message,
                    'mobile_number': partner_obj.telephone_number,
                }
                print('send cread for asp##########')

                send_sms(**msg_kwargs)
                print('send cread for asp##########')

                # Vendor register admin email function

                admin_email_list = []
                admin_list = User.objects.filter(is_superuser=True, is_staff=True).values_list('email', flat=True)

                for i in admin_list:
                    admin_email_list += [i]

                vendor_admin_email = {
                    'mail_subject': 'TakeRentPe - New ASP Register',
                    'mail_template': 'partner/emails/vendor_register_admin_email.html',
                    'mail_to': admin_email_list,
                    'mail_context': {
                        'vendor': user_obj, 'email_id': user_obj.email, 'pwd': pwd,
                        'domain': current_site.domain,'partner_obj':partner_obj,
                        'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(),
                        'token': account_activation_token.make_token(user_obj),
                    }
                }

                send_email(**vendor_admin_email)

                messages.success(
                    request, 'Your account is register successfully. Your account is under review, Once your account is reviewed we will let you know.'
                )
                return redirect('/')

            except Exception as e:
                import os
                import sys
                print('-----------in exception----------')
                print(e.args)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

                messages.error(request, 'Something went wrong.')
                return redirect('/')

        else:
            pass

        return render(request, self.template_name, {'form':form_partner_obj,'form_user':form_user_obj})


class UpdateVendorView(View):

    template_name = 'customer/vendor/vendor_form.html'
    form_class = VendorUpdateForm

    def get(self, request, *args, **kwargs):

        # check for valid vendor-user combination
        try:
            vendor = Partner.objects.get(id=kwargs.get('vendor_id'), users=request.user)
        except:
            messages.error(self.request,' Something went wrong.')
            return redirect('/')

        form = self.form_class(instance=vendor)

        context = {
            'vendor': vendor,
            'form': form
        }

        return render(
            self.request, self.template_name, context=context
        )

    def post(self, request, *args, **kwargs):

        # check for valid vendor-user combination
        try:
            vendor = Partner.objects.get(id=kwargs.get('vendor_id'), users=request.user)
        except:
            messages.error(self.request, ' Something went wrong.')
            return redirect('/')

        form = self.form_class(self.request.POST, instance=vendor)

        if form.is_valid():

            return self.is_valid(form)

        return self.is_invalid(form, vendor)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()

        messages.success(self.request, 'Profile updated successfully.')
        return redirect('customer:profile-view')

    def is_invalid(self, form, vendor):

        context = {
            'vendor': vendor,
            'form': form
        }

        return render(self.request, self.template_name, context=context)


def email_activate(request, uidb64, token):

    """
    Vendor email activation method
    To Do:
    Check usages
    """

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            return HttpResponse('Thank you for your email confirmation.')
        else:
            return HttpResponse('Your account is already activated.')
    except:
        return HttpResponse('Something went wrong!')


def state_ajax(request):

    """
    Ajax method to return state list.
    """

    if request.is_ajax():

        try:

            country_id = request.GET['country_id']
            state_list = State.objects.filter(country=country_id).order_by('state_name')

            results = []
            for i in state_list:
                state_json = {}
                state_json['text'] = i.state_name
                state_json['id'] = i.id
                results.append(state_json)

            data = json.dumps(results)
            mimetype = 'application/json'

            return HttpResponse(data, mimetype)

        except Exception as e:

            return HttpResponse('Ajax_State_Error')


def city_ajax(request):

    """
    Ajax method to return list of cities.
    """

    if request.method == 'GET':

        try:

            state_id = request.GET.get('state_name')
            city_list = City.objects.filter(state_id=state_id).order_by('city_name')

            results = []
            for i in city_list:
                city_json = {}
                city_json['text'] = i.city_name
                city_json['id'] = i.id
                results.append(city_json)
            data = json.dumps(results)

            mimetype = 'application/json'

            return HttpResponse(data, mimetype)

        except Exception as e:
            return HttpResponse('Ajax_City_Error')


def search_filter_ajax(request):

    """
    Ajax search filter.
    """

    if request.is_ajax():

        q = request.GET.get('term', '')
        product_list = Product.objects.filter(title__icontains=q.lower(), is_approved='Approved',is_deleted=False).order_by('title')

        product_list_x = Product.objects.filter(is_approved='Approved',is_deleted=False).order_by('title')
        category_list_x = Category.objects.all()

        results_list = list(chain(product_list_x,category_list_x))

        results = []
        for i in product_list_x:
            product_list_json = {}
            product_list_json = i.title
            results.append(product_list_json)
        data = json.dumps(results)
        mimetype = 'application/json'

        return HttpResponse(data, mimetype)


def partner_import(request):

    """
    Method to import vendors
    """

    if request.method == 'POST':
        csv_f = request.FILES['a']
        partner_obj = resources.modelresource_factory(model=Partner)()

        file_data = csv_f.read().decode("utf-8")
        lines = file_data.split("\n")
        for line in lines:
            fields = line.split(",")
            dataset = tablib.Dataset(fields,
                                     headers=['id','name', 'pan_number', 'vat_number', 'telephone_number',
                                              'email_id', 'address_line_1', 'address_line_2', 'country',
                                              'state', 'city', 'pincode', 'categories'])

            response = partner_obj.import_data(dataset, dry_run=False)

    return render(request, 'partner/import_partner.html')


def partner_export(request):

    """
    Export partner
    """

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="/vendor_template.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['id','Full Name', 'Email Address', 'PAN Number', 'VAT Number',
         'Contact Number', 'Address Line 1', 'Address Line 2', 'Country', 'State', 'City',
         'Pincode', 'Categories'
         ]
    )

    return response

from django.core.mail import send_mail

def test_email(request):

    send_mail(
        'Test email',
        'Hello, This is testing email.',
        'rmtest08.gmail.com',
        ['m.dhanwate@splendornet.com'],
        fail_silently=False,
    )

    return HttpResponse("Done")


def check_cron_view(request):

    check_cron.delay()

    return HttpResponse('done')