from django.urls import path

from .views import change_asp,delete_order


urlpatterns = [
    path("orders/<int:number>/delete/",delete_order, name='order-delete'),
     path("orders/<int:order_number>/change-asp/<int:partner_id>/",change_asp, name='order_change_asp'),
     
]