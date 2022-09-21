from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CustomOrder.order.models import Order, Line
from CustomPartner.partner.models import MultiDB
from django.http import JsonResponse


# Create your views here.

@login_required
def delete_order(request,number=None):
    order=Order.objects.get(number=number)
    order.delete()
    print(f"Order {number} deleted Successully")
    messages.success(request,"Order deleted successfully")
    return redirect('/dashboard/orders/')

@login_required
def change_asp(request,order_number=None,partner_id=None):
    if request.method=="GET":

        assigned_asp= MultiDB.objects.filter(frontliener=471)

        return JsonResponse({'text':assigned_asp.frontliener.last().name},safe=False)


    if request.method=="POST":
        changed_asp=request.POST['update_asp_id']
        changed_asp_name=request.POST['update_asp_name']
        partner_sku=request.POST['partner_sku']

        order=Order.objects.get(number=order_number)
        order_updated=Line.objects.get(order=order.id,patner=partner_id,partner_sku=partner_sku)
        order_updated.allocated_vendor=changed_asp
        order_updated.allocated_vendor_name=changed_asp_name

        order_updated.save()

        return redirect('/dashboard/orders/'+order_number+'/')
