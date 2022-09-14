# python imports
import datetime

# django imports
from django.shortcuts import HttpResponse
from django.contrib import messages

# packages imports
from oscar.core.loading import get_classes, get_model
from oscar.core.compat import get_user_model

# internal imports
Notes = get_model('customer', 'Notes')
User = get_user_model()


def add_admin_notes(request):

    try:

        data = request.GET

        note_details = data.get('note_details')
        note_start_date = data.get('note_start_date')
        notes_time = data.get('notes_time')

        if note_details is None or note_start_date is None or notes_time is None:
            return HttpResponse('IN_SERVER')

        # 2020-10-3012:14
        start_date_str = note_start_date + ' ' + notes_time
        start_date_object = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M')

        Notes.objects.create(
            created_by=request.user, note=note_details,
            start_date=start_date_object,
        )

        messages.success(request, "Note saved successfully")
        return HttpResponse('TRUE')

    except Exception as e:

        messages.error(request, "Something went wrong")
        return HttpResponse('IN_SERVER')