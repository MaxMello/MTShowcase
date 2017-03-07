from django import forms

from apps.project.validators import MimeTypeValidator, ALLOWED_AUDIO_MIME_TYPES


class ImageFormField(forms.Form):
    def __init__(self, field_name, *args, **kwargs):
        super(ImageFormField, self).__init__(*args, **kwargs)
        self.fields[field_name] = forms.ImageField(required=True, allow_empty_file=False)


class AudioFileField(forms.Form):
    def __init__(self, field_name, *args, **kwargs):
        super(AudioFileField, self).__init__(*args, **kwargs)
        self.fields[field_name] = forms.FileField(
            required=True,
            allow_empty_file=False,
            validators=[MimeTypeValidator(ALLOWED_AUDIO_MIME_TYPES)])
