from django.contrib import admin
from django.shortcuts import render
from .models import ServiceOrders

# Register your models here.
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'name','mobile', 'email','added_date')
    #list_display_links = ('trek_location_details_id', 'treking_schedule_details_id','name','mobile', 'email', 'is_read', 'added_date', 'modified_date')
    search_fields = ('product', 'name','mobile', 'email','added_date')
    list_per_page = 10
    list_filter = ('product', 'name','mobile', 'email','added_date')

admin.site.register(ServiceOrders,ServiceOrderAdmin)
