from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# to update vendor password
def updateVendorPassword(request):
    getUsers = User.objects.filter(is_superuser__exact=False, is_staff__exact=True, is_active=True)
    for users in getUsers:
        print(users.email)
        User.objects.filter(is_superuser__exact=False, is_staff__exact=True, is_active=True,pk__exact=users.id).update(password=make_password('#takerentpe2019#'))
    return HttpResponse('*****************Updated successfully****************')