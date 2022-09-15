from django.urls import path

from .views import delete_order


urlpatterns = [
    path("orders/<int:number>/delete/",delete_order, name='order-delete'),

]