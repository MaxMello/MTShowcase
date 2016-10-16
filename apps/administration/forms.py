from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from django import forms


class InviteForm(forms.Form):
    invite_mail = forms.EmailField(required=True, validators=lambda x: str(x).endswith('@haw-hamburg.de'))

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            ButtonHolder(
                Submit('invite', 'Einladen', css_class='btn-primary')
            )
        )
