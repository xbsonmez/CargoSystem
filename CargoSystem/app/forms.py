from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField, SetPasswordForm
from django.utils.translation import gettext, gettext_lazy as _
from .models import IsikCargos

User = get_user_model()

class AddCargoForm(forms.Form):
    to_who   = forms.IntegerField(label='Receiver TC Number', min_value=10000000000, max_value=99999999999)
    from_who = forms.CharField(max_length=50)

class LoginForm(forms.Form):
    username=forms.CharField(label='username',max_length=55)
    password=forms.CharField(label='password',max_length=55)

class UserCreateForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'username_exists': _("Username is already exists."),
        'email_exists': _("Email is already exists."),
        'password_character': _("Password should be in a character range 6 and 30."),
        'username_character': _("Username should be in a character range 6 and 30."),
    }

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        strip=False,
    )

    password2 = forms.CharField(
        label=_("Password again"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    field_order = [
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'password2',
        'user_type',
        'tc_no'
    ]

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Username'),
            'autocomplete': 'off',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': _('Email'),
            'class' : 'form-control',
        })
        self.fields['password'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Password'),
        })
        self.fields['password2'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Password Again'),
        })
        self.fields['tc_no'].widget.attrs.update({
            'class' : 'form-control',
        })
        self.fields['first_name'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('First Name'),
        })
        self.fields['last_name'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Last name'),
        })
        self.fields['user_type'].widget.attrs.update({
            'class' : 'form-control',
            'id': 'userType',
            'placeholder': _('Job type'),
        })

    class Meta:
        model = User
        fields = {
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'user_type',
            'tc_no'
        }

        widgets = {
            'password': forms.PasswordInput,
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if len(username) < 6 or len(username) > 30:
            raise forms.ValidationError(self.error_messages['username_character'])
        if qs.exists():
            raise forms.ValidationError(self.error_messages['username_exists'])
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError(self.error_messages['email_exists'])
        return email

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        if len(password) < 6 or len(password) > 30:
            raise forms.ValidationError(self.error_messages['password_character'])
        return password

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        type = self.cleaned_data.get("user_type")
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        return user

class AdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Your password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = {
            'email',
        }

    def clean_password2(self):
        # Checks the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(AdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label='Password',
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        ),
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def clean_tc_no(self):
        tc_no = self.cleaned_data.get('tc_no')
        qs = User.objects.filter(tc_no=tc_no)
        if qs.exists():
            raise forms.ValidationError(_("TC NO is already exists."))
        return tc_no