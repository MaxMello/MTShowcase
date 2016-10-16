from django.forms import ModelChoiceField
from apps.user.models import Social


class UserSocialModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        if isinstance(obj, Social):
            return obj.display_name
