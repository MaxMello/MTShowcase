from apps.authentication.models import RegistrationProfile
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, **options):
        """
        call via 'python manage.py cleanexpired'

        Delete all expired user from the db. This will delete all
        Registrationprofiles including AuthEmailUser relations.
        """
        RegistrationProfile.objects.delete_expired_users()