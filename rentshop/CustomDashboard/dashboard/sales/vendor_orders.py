from django.shortcuts import HttpResponse
from django.views import generic


class VendorOrders(generic.View):

    def get(self, request, *args, **kwargs):

        return HttpResponse('O')
