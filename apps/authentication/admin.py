from django.contrib import admin
from .models import AuthEmailUser, RegistrationProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms


class AuthUserCreationForm(forms.ModelForm):
    """
    Form to create new users in admin area.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = AuthEmailUser
        fields = ('email',)

    def clean_password2(self):
        # Check password matching.
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format.
        user = super(AuthUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AuthUserChangeForm(forms.ModelForm):
    """
    Form to update user information.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AuthEmailUser
        fields = ('email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AuthEmailUserAdmin(BaseUserAdmin):
    # forms to add or change users
    form = AuthUserChangeForm
    add_form = AuthUserCreationForm

    # define fields to display in the user model
    list_display = ('email', 'first_name', 'last_name', 'registration_date', 'is_staff')
    list_filter = ('is_staff',)

    fieldsets = fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Person', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


class RegistrationAdmin(admin.ModelAdmin):
    actions = ['activate_users', 'resend_activation_email']
    list_display = ('user', 'activation_key_expired')
    raw_id_fields = ['user']
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def activate_users(self, request, queryset):
        """
        Activate the selected users, if they are not already
        activated.
        """
        for profile in queryset:
            RegistrationProfile.objects.activate_user(profile.activation_key)

    def resend_activation_email(self, request, queryset):
        """
        Re-send activation email for non activated or expired user.
        """
        for profile in queryset:
            if not profile.activation_key_expired():
                profile.send_activation_email()


admin.site.register(AuthEmailUser, AuthEmailUserAdmin)
admin.site.register(RegistrationProfile, RegistrationAdmin)
