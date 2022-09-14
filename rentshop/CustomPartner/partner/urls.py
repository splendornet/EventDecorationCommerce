# django imports
from django.conf.urls import url
from django.views.generic import TemplateView

# 3rd party imports
from oscar.core.loading import get_class

# internal imports
from .views import email_activate, partner_export, partner_import


AddPartner = get_class('partner.views', 'AddPartner')
UpdateVendorView = get_class('partner.views', 'UpdateVendorView')


urlpatterns = [

    url(r'^add/', AddPartner.as_view(), name='register-vendor'),
    url(r'^update-vendor/(?P<vendor_id>\d+)/', UpdateVendorView.as_view(), name='vendor-update'),

    url(r'^success/$', TemplateView.as_view(template_name='partner/PartnerSuccess.html')),

    url(r'^partner/', TemplateView.as_view(template_name='partner/cafe.html')),
    url(r'^email_activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', email_activate, name='email_activate'),

    url(r'^export', partner_export, name='partner_export'),
    url(r'^import', partner_import, name='partner_import')
]