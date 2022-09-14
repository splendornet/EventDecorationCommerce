from django import forms
from oscar.core.loading import get_class, get_model

Admin_HeaderMenu = get_model('HeaderMenu', 'Admin_HeaderMenu')

from django.forms.widgets import ClearableFileInput

class MyClearableFileInput(ClearableFileInput):
    initial_text = 'currently'
    input_text = 'change'
    clear_checkbox_label = ''

class MyOfferUploadImages(forms.ModelForm):
    menu_image = forms.ImageField(required=False, widget=MyClearableFileInput)
    class Meta:
        model = Admin_HeaderMenu
        fields = ('menu_image',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(MyOfferUploadImages, self).__init__(*args, **kwargs)

