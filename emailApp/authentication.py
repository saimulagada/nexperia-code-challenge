from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Use email (which is passed as 'username' here) for authentication
            user = User.objects.get(email=username)  # 'username' is actually the email
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
