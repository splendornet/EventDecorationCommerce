# import python
import string

# django imports
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

# 3rd party imports
from oscar.apps.customer.forms import EmailUserCreationForm, UserForm, EmailAuthenticationForm
from oscar.core.loading import get_class, get_model
from captcha.fields import CaptchaField
from oscar.core.compat import (existing_user_fields, get_user_model)

# internal imports
User = get_user_model()
custom_profile = get_model('customer', 'CustomProfile')
from django.contrib.auth.forms import PasswordChangeForm


def generate_username():

    letters = string.ascii_letters
    allowed_chars = letters + string.digits + '_'
    uname = get_random_string(length=30, allowed_chars=allowed_chars)

    try:
        User.objects.get(username=uname)
        return generate_username()
    except User.DoesNotExist:
        return uname


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = 'form-control  mb-25'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control  mb-25'
        self.fields['old_password'].widget.attrs['class'] = 'form-control  mb-25'


class CustomEmailAuthenticationForm(EmailAuthenticationForm):

    """
    Oscar extended email auth login form.
    """

    def clean(self):
        
        """
        Method to validate user
        :return: validation
        """

        _user = None
        _status = 0
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:

            try:

                _user = User.objects.get(email=username)

                if _user.is_staff:
                    if not _user.is_active:
                        _status = 4
                else:
                    if not _user.is_active and not _user.profile_user.is_blocked:
                        _status = 1
                    elif not _user.is_active and _user.profile_user.is_blocked:
                        _status = 2
                    else:
                        print('#01')


            except Exception as e:
                pass

            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:

                if _status == 0:
                    raise forms.ValidationError('Please enter valid username or password')
                elif _status == 1:
                    raise forms.ValidationError('Please activate your account, we have sent you activation link on your registered email id.')
                elif _status == 2:
                    raise forms.ValidationError('Account is disabled. Please contact admin.')
                elif _status == 4:
                    raise forms.ValidationError('Account is disabled. Please contact admin.')
                else:
                    raise forms.ValidationError('Please enter valid username or password')

            else:
                self.confirm_login_allowed(self.user_cache)


class CustomEmailUserCreationForm(EmailUserCreationForm):

    password1 = forms.CharField(max_length=15,label=_('Password'), widget=forms.PasswordInput,)
    password2 = forms.CharField(max_length=15, label=_('Confirm password'), widget=forms.PasswordInput,)
    first_name = forms.CharField(max_length=20, required=True,validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid first name.')])
    last_name = forms.CharField(max_length=20, required=True,validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid last name.')])

    # captcha = CaptchaField()
    mobile_number = forms.CharField(max_length=13, min_length=10, required=True,validators=[RegexValidator('^([0]|\+91)?[789]\d{9}$', message='Enter a valid mobile number.')])

    class Meta:
        model = User
        fields = ('email','password1','password2','last_name','first_name','mobile_number',)

    def clean_mobile_number(self):

        number = self.cleaned_data['mobile_number']
        if custom_profile.objects.filter(mobile_number__iexact=number).exists():
            raise forms.ValidationError(
                _("A user with that mobile number address already exists."))
        return number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if 'username' in [f.name for f in User._meta.fields]:
            user.username = generate_username()
        if commit:
            user.is_active = False
            user.save()
        return user


class CustomUserForm(UserForm):

    first_name = forms.CharField(max_length=20, required=False, validators = [RegexValidator('^([A-Za-z])+$', message='Enter a valid first name.')])
    last_name = forms.CharField(max_length=20, required=False, validators = [RegexValidator('^([A-Za-z])+$', message='Enter a valid last name.')])
    mobile_number = forms.CharField(max_length=10, min_length=10, required=True,validators=[RegexValidator('^([0-9])+$', message='Enter a valid mobile number.')])

    def clean_mobile_number(self):

        number = self.cleaned_data['mobile_number']
        if custom_profile.objects.filter(mobile_number__iexact=number).exclude(user_id=self.user.id).exists():
            raise forms.ValidationError(
                _("A user with that mobile number address already exists."))
        return number


class CustomUserUpdateForm(UserForm):

    """
    Oscar extended form to update user profile.
    """

    mobile_number = forms.CharField(max_length=10, min_length=10, required=True,validators=[RegexValidator('^([0-9])+$', message='Enter a valid mobile number.')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control  mb-25'
        self.fields['first_name'].widget.attrs['class'] = 'form-control  mb-25'
        self.fields['last_name'].widget.attrs['class'] = 'form-control  mb-25'

    def clean_mobile_number(self):

        number = self.cleaned_data['mobile_number']
        if custom_profile.objects.filter(mobile_number__iexact=number).exclude(user_id=self.user.id).exists():
            raise forms.ValidationError(
                _("A user with that mobile number address already exists."))
        return number


class CustomUserUpdate(forms.ModelForm):

    mobile_number = forms.CharField(max_length=10, min_length=10, required=True,validators=[RegexValidator('^([0-9])+$', message='Enter a valid mobile number.')])

    def clean_mobile_number(self):

        number = self.cleaned_data['mobile_number']
        if custom_profile.objects.filter(mobile_number__iexact=number).exists():
            raise forms.ValidationError(
                _("A user with that mobile number address already exists."))
        return number

    class Meta:
        model = custom_profile
        fields = "__all__"


class CustomPasswordChangeForm(PasswordChangeForm):

    """
    Oscar extended form to update user profile.
    """

    # mobile_number = forms.CharField(max_length=10, min_length=10, required=True,validators=[RegexValidator('^([0-9])+$', message='Enter a valid mobile number.')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control mb-10'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control mb-10'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control mb-10'


    # def clean_mobile_number(self):
    #
    #     number = self.cleaned_data['mobile_number']
    #     if custom_profile.objects.filter(mobile_number__iexact=number).exclude(user_id=self.user.id).exists():
    #         raise forms.ValidationError(
    #             _("A user with that mobile number address already exists."))
    #     return number


'''
from oscar.core.loading import get_class, get_model, get_profile_class
from oscar.apps.customer.utils import get_password_reset_url, normalise_email
from oscar.apps.customer.forms import UserAndProfileForm
from django.core.exceptions import ValidationError



Profile = get_profile_class()
if Profile:  # noqa (too complex (12))

    class CustomUserAndProfileForm(UserAndProfileForm):

        def __init__(self, user, *args, **kwargs):
            try:
                instance = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                # User has no profile, try a blank one
                instance = Profile(user=user)
            kwargs['instance'] = instance

            super().__init__(*args, **kwargs)

            # Get profile field names to help with ordering later
            profile_field_names = list(self.fields.keys())

            # Get user field names (we look for core user fields first)
            core_field_names = set([f.name for f in User._meta.fields])
            user_field_names = ['email']
            for field_name in ('first_name', 'last_name'):
                if field_name in core_field_names:
                    user_field_names.append(field_name)
            user_field_names.extend(User._meta.additional_fields)

            # Store user fields so we know what to save later
            self.user_field_names = user_field_names

            # Add additional user form fields
            additional_fields = forms.fields_for_model(
                User, fields=user_field_names)
            self.fields.update(additional_fields)

            # Ensure email is required and initialised correctly
            self.fields['email'].required = True

            # Set initial values
            for field_name in user_field_names:
                self.fields[field_name].initial = getattr(user, field_name)

            # Ensure order of fields is email, user fields then profile fields
            self.fields.keyOrder = user_field_names + profile_field_names

        class Meta:
            model = Profile
            exclude = ('user',)

        def clean_email(self):
            email = normalise_email(self.cleaned_data['email'])

            users_with_email = User._default_manager.filter(
                email__iexact=email).exclude(id=self.instance.user.id)
            if users_with_email.exists():
                raise ValidationError(
                    _("A user with this email address already exists"))
            return email

        def save(self, *args, **kwargs):
            user = self.instance.user

            # Save user also
            for field_name in self.user_field_names:
                setattr(user, field_name, self.cleaned_data[field_name])
            user.save()

            return super().save(*args, **kwargs)

    ProfileForm = CustomUserAndProfileForm
else:
    ProfileForm = UserForm
'''