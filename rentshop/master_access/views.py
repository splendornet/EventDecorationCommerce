from django.shortcuts import render,redirect
from django.contrib import messages
from CustomOrder.order.models import Order


# Create your views here.


def delete_order(request,number=None):
    order=Order.objects.get(number=number)
    order.delete()
    print(f"Order {number} deleted Successully")
    # messages.success(request,"Order deleted successfully")
    return redirect('/dashboard/orders/')