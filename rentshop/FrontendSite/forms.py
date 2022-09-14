from django import forms
from django.core.files.images import get_image_dimensions
from .models import *
from PIL import Image
from oscar.forms.widgets import DateTimePickerInput, ImageInput


def validate_image_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Please upload only .jpg, jpeg , .svg or .png image.')

from django.forms.widgets import ClearableFileInput
class MyClearableFileInput(ClearableFileInput):
    initial_text = ''
    input_text = ''
    clear_checkbox_label = ''

class SliderImageForm(forms.ModelForm):
    slider_image = forms.ImageField()
    mobile_view_image = forms.FileField(widget= MyClearableFileInput , required= False, validators=[validate_image_extension])


    class Meta:
        model = SliderImage
        fields = ('slider_image','mobile_view_image','is_provide_path_link','path_link','cta_button_text',)
        widgets = {
            'slider_image': ImageInput(),
        }

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """
        super(SliderImageForm, self).__init__(*args, **kwargs)
        self.fields['path_link'].widget.attrs['class'] = 'form-control'
        self.fields['cta_button_text'].widget.attrs['class'] = 'form-control'
        self.fields['path_link'].required = False
        self.fields['cta_button_text'].required = False
        self.fields['mobile_view_image'].required = False
        self.fields['cta_button_text'].label = "CTA button text"
        self.fields['path_link'].label = "Path"
        # self.fields['image'].widget = MyClearableFileInput



    def clean_image(self):
        image = self.cleaned_data['slider_image']
        if not image:
            raise forms.ValidationError('no img')
        else:
            w,h = get_image_dimensions(image)
            if w <=500 and h <=500:
                raise forms.ValidationError('Enter valid image dimensions')

        return image