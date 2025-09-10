from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.compat import gettext_lazy as _


class CustomJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """
    Overrides Rest Framework authentication logic.
    """

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's auth_id
        """

        auth_id = self.jwt_get_username_from_payload(payload)

        if not auth_id:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            UserModel = get_user_model()
            # Prefetch groups to optimize resolver_requires_role and resolver_requires_roles decorator.
            # This is done so that we don't have to query user.groups each time
            # the decorator is executed.
            user = UserModel.objects.prefetch_related('groups').get(auth0_id=auth_id)
        except UserModel.DoesNotExist:
            return None

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user