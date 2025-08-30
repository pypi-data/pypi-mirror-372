from piprints.main.models import User
import datetime

class UserBackend(object):
    """
    Authenticates against piprints.main.models.User.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass

class ImpersonificationBackend(object):
    """
    logs in a staff user impersonificating another given user
    """
    def authenticate(self, request, admin=None, password=None, as_user=None):
        try:
            admin = User.objects.get(is_staff=True,is_active=True,username=admin)
            user = User.objects.get(username=as_user)
            if admin.check_password(password):
                user.impersonificated_by=admin
                return user
        except User.DoesNotExist:
            pass


    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
