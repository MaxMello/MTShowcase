from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
from django import forms
from django.contrib.auth import password_validation, authenticate
from django.utils.translation import ugettext_lazy as _

from .models import AuthEmailUser





class RegistrationForm(forms.ModelForm):
    prefix = "signup"
    error_messages = {
        'password_mismatch': "Die beiden Passwörter sind nicht identisch.",
        'duplicate_email': "Ein Nutzer mit dieser Email existiert bereits.",
    }

    password1 = forms.CharField(label=_("Password"),
                                strip=False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                strip=False)

    class Meta:
        model = AuthEmailUser
        fields = ('email',)
        localized_fields = ('email',)
        labels = {
            'email': _('Email')
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            'password1',
            'password2',
            ButtonHolder(
                Submit('register', 'Registrieren', css_class='btn-primary')
            )
        )

    def clean_email(self):
        # Clean form email for better error message.

        email = self.cleaned_data["email"]
        try:
            # check if email does not exists
            # otherwise raise duplicate error
            AuthEmailUser.objects.get(email=email)
        except AuthEmailUser.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        # check password matching
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.email = self.cleaned_data.get('email')
        # pw validation checking, seeing pw validator in settings.py
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    prefix = "login"
    error_messages = {
        'invalid_login': "Bitte gib eine gültige Email und ein korrektes Passwort ein.",
        'inactive': "Dieser Account ist inaktiv. Hast du deine Email bestätigt?",
    }

    email = forms.EmailField(label=_('Email'), widget=forms.TextInput, localize=True)
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput, localize=True)
    remember_me = forms.BooleanField(label='Eingeloggt bleiben', required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            'password',
            'remember_me',
            HTML('<p><a href="{}">Passwort vergessen?</a></p>'.format(
                "{% url 'home' %}")),
            ButtonHolder(
                Submit('login', 'Login', css_class='btn-primary')
            )
        )

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            # redundant check for error handling
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(user)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
