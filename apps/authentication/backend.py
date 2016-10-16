from django.contrib.auth import get_user_model


class EmailBackend(object):

    def authenticate(self, email=None, password=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except UserModel.DoesNotExist:
            return None
