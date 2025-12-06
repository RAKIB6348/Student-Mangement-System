from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UserIdBackend(ModelBackend):
    """
    Authenticate users against the custom user model using the generated user_id.
    """

    def authenticate(self, request, username=None, password=None, user_id=None, **kwargs):
        user_identifier = user_id or username
        if not user_identifier or not password:
            return None

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(user_id=user_identifier)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
