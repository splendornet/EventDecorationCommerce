from django.shortcuts import render,redirect
from django.contrib import messages


# Create your views here.


def delete_order(request,number=None):
    print("Success")
    messages.success(request,"Order deleted successfully")
    return redirect('/dashboard/orders/')