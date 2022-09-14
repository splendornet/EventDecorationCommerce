from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
    url(r'^service-enquiry/(?P<productId>\d+)/', service_enquiry_ajax, name='service-enquiry'),
    url(r'^service-order-list/', ServiceOrderListView.as_view(), name='service-order-list'),
    url(r'^export_service_order/', export_service_order, name='export_service_order')
]