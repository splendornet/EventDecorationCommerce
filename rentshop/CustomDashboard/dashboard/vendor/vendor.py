# import python
import datetime
import json
# django imports
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMessage

# internal imports
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model
from . import vendor_forms as vendor_form

PartnerUpdateForm = get_class('partner.forms','PartnerUpdateForm')
Partner = get_model('partner', 'Partner')
VendorProductStatus = get_model('partner', 'VendorProductStatus')

Product = get_model('catalogue', 'Product')
User = get_user_model()
send_sms = get_class('RentCore.email', 'send_sms')

class CustomPartnerManageView(generic.UpdateView):

    """
    Vendor manage/update view.
    """

    template_name = 'dashboard/partners/partner_manage.html'
    form_class = vendor_form.PartnerUpdateForm

    success_url = reverse_lazy('dashboard:partner-list')

    def get_object(self, queryset=None):

        self.partner = get_object_or_404(Partner, pk=self.kwargs['pk'])
        self.user = self.partner.users.all()

        return self.partner

    def get_initial(self):

        country = 1
        partner_obj = Partner.objects.get(id=self.partner.id)

        return {
            'name': self.partner.name,
            'address_line_1': self.partner.address_line_1,
            'address_line_2': self.partner.address_line_2,
            'telephone_number': self.partner.telephone_number,
            'email_id': self.partner.email_id,
            'country': country,
            'state': self.partner.state_id,
            'city': self.partner.city_id,
            'pincode': self.partner.pincode,
            'categories': partner_obj.categories,
            'business_name': self.partner.business_name,
            'alternate_mobile_number': self.partner.alternate_mobile_number,
        }

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['partner'] = self.partner
        ctx['title'] = self.partner.name

        self.user = self.partner.users.all()

        for vendorUser in self.user:
            if vendorUser.is_active:
                ctx['userIsActive'] = True
            else:
                ctx['userIsActive'] = False

        ctx['users'] = self.partner.users.all()

        return ctx

    def form_valid(self, form):

        messages.success(self.request, _("Partner '%s' was updated successfully.") % self.partner.name)

        self.partner.name = form.cleaned_data['name']
        is_active = form.cleaned_data['user_active']



        user_update_obj = User.objects.get(id__in=self.user)

        if is_active and not user_update_obj.is_active:
            qs = Product.objects.all()
            partner_obj = Partner.objects.get(users=user_update_obj)
            vendor_data = VendorProductStatus.objects.filter(vendor = partner_obj)
            if vendor_data:
                obj = vendor_data.last()
                data = json.loads(obj.product_status)

                qs_obj = qs.filter(stockrecords__partner=partner_obj)
                for prod in data:
                    qs.filter(id=prod['id'],title=prod['productName']).update(is_approved = prod['productStatus'])
                vendor_data.delete()

        user_update_obj.is_active = is_active
        user_update_obj.email = form.cleaned_data['email_id']
        user_update_obj.username = form.cleaned_data['email_id']

        user_update_obj.save()

        if user_update_obj.is_active == True and not self.partner.updated_date:
            try:

                current_site = Site.objects.get_current()
                mail_subject = 'TakeRentPe - ASP Account Activation.'
                message = render_to_string(
                    'customer/emails/thank_you_email.html',
                    {
                        'vendor': user_update_obj,
                        'email_id': user_update_obj.email,
                        'domain': current_site.domain,
                    }
                )

                to_email = user_update_obj.email
                from_email = settings.FROM_EMAIL_ADDRESS
                email = EmailMessage(mail_subject, message, from_email, [to_email])
                email.content_subtype = "html"
                email.send()

                # send sms code WELCOME & SMS ID VERIFICATION SMS
                message = 'Welcome to the family ' + str(user_update_obj.first_name) + ' Thank you for being an ASP with our Family. We’ll always look forward for amazing things in future! Happy celebranto, Take Rent Pe'
                msg_kwargs = {
                    'message': message,
                    'mobile_number': self.partner.telephone_number,
                }
                print('send wel for asp##########@@')
                send_sms(**msg_kwargs)
                print('send wel for asp##########@@')

            except:
                pass

        self.partner.updated_date = datetime.datetime.now()

        qs = Product.objects.all()
        partner_obj = Partner.objects.get(users=user_update_obj)

        if not user_update_obj.is_active:
            vendor_list = []
            qs_obj = qs.filter(stockrecords__partner=partner_obj)
            for item in qs_obj:
                vendor_dict = dict()
                vendor_dict['id'] = item.id
                vendor_dict['productName'] = item.title
                vendor_dict['productStatus'] = item.is_approved


                vendor_list.append(vendor_dict)
            data = json.dumps(vendor_list)
            VendorProductStatus.objects.create(
                vendor = partner_obj,
                product_status = data,
            )
            qs_obj = qs.filter(stockrecords__partner=partner_obj).update(is_approved='Pending')

        self.partner.save()
        return super().form_valid(form)