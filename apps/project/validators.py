from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from urllib.parse import urlparse
import magic

from apps.user.models import Social

url_validator = URLValidator()


class UrlToSocialMapper(object):
    @staticmethod
    def return_social_from_url_or_none(url):
        """
        Maps or creates a valid URL to one of the available socials (provider).
        :param url: url to map/create from
        :return: the found social entry or default social (name='link')
        """
        try:
            url_validator(url)
            hostname = urlparse(url).hostname
            for social in Social.objects.all():
                if social.name in hostname:
                    return social

        except ValidationError:
            return None
        else:
            return Social.objects.filter(name='link').first()


ALLOWED_AUDIO_MIME_TYPES = ['audio/mp3', 'audio/mp4', 'audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/webm', 'audio/aac']
ALLOWED_VIDEO_MIME_TYPES = ['video/mp4', 'video/ogg', 'video/webm']


class MimeTypeValidator(object):
    def __init__(self, mime_types):
        self.mime_types = mime_types

    def __call__(self, data):
        try:
            if hasattr(data, 'temporary_file_path'):
                file = data.temporary_file_path()
            else:
                if hasattr(data, 'read'):
                    file = BytesIO(data.read())
                else:
                    file = BytesIO(data['content'])

            mime = magic.from_buffer(open(file, "rb").read(32768), mime=True)
            print("file mime" + mime)
            if mime not in self.mime_types:
                raise ValidationError('%s not accepted type' % data)
        except AttributeError as e:
            raise ValidationError('Value could not be validated' + str(e))


def validate_empty(test_str):
    test_str = test_str.strip()
    if not test_str:
        return ''
    return test_str
