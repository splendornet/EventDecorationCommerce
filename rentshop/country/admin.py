from django.contrib import admin
from country.models import *

# Register your models here.
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)