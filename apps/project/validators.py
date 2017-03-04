from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from urllib.parse import urlparse

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
            return Social.objects.get(name='link')
