from django.contrib.auth import backends
from chat.models import UserProxyModel


class ModelBackend(backends.ModelBackend):
    '''
    Extending to provide a proxy for user
    '''

    def get_user(self, user_id):
        try:
            return UserProxyModel.objects.get(pk=user_id)
        except UserProxyModel.DoesNotExist:
            return None
