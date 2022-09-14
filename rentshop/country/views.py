# python imports
import json

# django imports
from django.shortcuts import HttpResponse

# internal imports
from .models import *


def get_cities(request):

    return HttpResponse('DONE')


def get_state_id(request):

    data = request.GET
    state_name = data.get('state_name')

    states = State.objects.filter(state_name=state_name)

    if states:
        return HttpResponse(states.last().id)

    return HttpResponse('1')
