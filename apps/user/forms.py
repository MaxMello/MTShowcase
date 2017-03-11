from apps.authentication.models import AuthEmailUser
from apps.user.fields import UserSocialModelChoiceField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML, Hidden
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import ModelForm
from apps.user.models import User, UserSocial, Social
from apps.project.models import ProjectMember


class MyPasswordChangeForm(PasswordChangeForm):
    """From to change the users password.

    To change the password, the user needs to pass his old password
    and then his new password.

    """

    def __init__(self, *args, **kwargs):
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('old_password', placeholder="Altes Passwort",
                  autofocus=""),
            Field('new_password1', placeholder="Neues Passwort"),
            Field('new_password2', placeholder="Neues Passwort (erneut)"),
            Submit('pass_change', 'Passwort ändern', css_class="btn-warning"),
        )
        self.fields['new_password1'].help_text = None


class AccountUserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AccountUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field('first_name'),
            Field('last_name'),
        )

    class Meta:
        model = AuthEmailUser
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname'
        }


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field('unique_name'),
        )

    class Meta:
        model = User
        fields = ['unique_name']
        labels = {
            'unique_name': "Username",
        }


class ProjectPrivacyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectPrivacyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            'display_username',
        )

    class Meta:
        model = ProjectMember
        fields = ['display_username']
        labels = {
            'display_username': ''
        }


class ShowClearNameForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShowClearNameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(
                "<label for='div_id_show_clear_name'>Soll dein Klarname (Vorname + Nachname) in Projekten/Profil angezeigt werden?</label>"),
            Field('show_clear_name')
        )

    class Meta:
        model = User
        fields = ['show_clear_name']
        labels = {
            'show_clear_name': 'Klarnamen anzeigen'
        }
        widgets = {
            'profile_img': forms.FileInput(),
        }

    def clean_show_clear_name(self):
        show_clear_name = self.cleaned_data['show_clear_name']
        if not show_clear_name:
            useralias = self.instance.alias
            if not useralias:
                raise forms.ValidationError("Der Anzeigename muss gesetzt sein")
        return show_clear_name


class UserSocialForm(ModelForm):
    social_list = UserSocialModelChoiceField(label="Socials", queryset=None, to_field_name='name', required=True)

    def __init__(self, user, *args, **kwargs):
        super(UserSocialForm, self).__init__(*args, **kwargs)
        self.fields['social_list'].queryset = Social.objects.all().exclude(
            id__in=UserSocial.objects.filter(user=user).values_list('social'))
        self.helper = FormHelper()
        self.helper.form_id = "social-form"
        self.helper.layout = Layout(
            HTML('<h5>Füge Social Verlinkung hinzu</h5>'),
            'social_list',
            'url',
            Submit('add', 'Add', css_class="btn-success"),
        )

    """
    def clean_url(self):
        url = self.cleaned_data['url']
        return url
    """

    class Meta:
        model = UserSocial
        fields = ['url']


class UserSocialEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserSocialEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "social-form"
        self.helper.layout = Layout(
            HTML('<h5>Social bearbeiten</h5>'),
            HTML('<h3>{{ socialname | capfirst }}</h3>'),
            Hidden(name='id-user-social', value="{{ id }}"),
            'url',
            Submit('update', 'Update', css_class="btn-success"),
            Submit('delete', 'Löschen', css_class="btn-warning"),
        )

    class Meta:
        model = UserSocial
        fields = ['url']
