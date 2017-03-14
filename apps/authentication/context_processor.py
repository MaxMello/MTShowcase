from MTShowcase import secrets
from .forms import LoginForm, RegistrationForm


def include_login_form(request):
    form = LoginForm()
    return {'login_form': form}


def include_register_form(request):
    form = RegistrationForm
    return {'register_form': form}


def include_production_flag(request):
    return {'production': secrets.production, "prod": secrets.prod}
