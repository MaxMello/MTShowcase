from django import forms


class ImageFormField(forms.Form):
    def __init__(self, field_name, *args, **kwargs):
        super(ImageFormField, self).__init__(*args, **kwargs)
        self.fields[field_name] = forms.ImageField(required=True)
