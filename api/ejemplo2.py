# serializers.py
from rest_framework import serializers, validators
from .models import Customer


def no_html_tags(value):
    if "<" in value or ">" in value or "=" in value:
        raise validators.ValidationError("HTML tags are not allowed.")


class LoginSerializer(serializers.ModelSerializer):
    """Serializer for handling logins only!"""

    email = serializers.EmailField(validators=[no_html_tags])
    password = serializers.CharField(write_only=True, validators=[no_html_tags])

    class Meta:
        model = Customer
        fields = ("email", "password")

# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import LoginSerializer
from .models import Customer


def get_tokens_for_user(user):
    """Generate refresh and access tokens for a given user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
def LoginApi(request):
    """View for handling login API"""
    if request.headers.get("myheader") != "login783743sdhdh$#536f3q523$@#Y#":
        return Response(
            {'error': "Page Not Found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        try:
            customer = Customer.objects.get(email=email)
            myuser = authenticate(email=email, password=password)

            if myuser and customer.email_verified:
                token = get_tokens_for_user(myuser)
                response_data = {
                    "customer_data": {
                        "id": customer.id,
                        "email": customer.email,
                        "name": customer.name,  # ajusta si tu modelo tiene este campo
                    },
                    "accessToken": token["access"],
                }
                return Response(response_data, status=status.HTTP_202_ACCEPTED)

            elif myuser is None and not customer.email_verified:
                return Response(
                    {'error': "Please verify your email in order to login!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            else:
                return Response(
                    {'error': "Incorrect email or password!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Customer.DoesNotExist:
            return Response(
                {'error': "Incorrect username or password!"},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        {'error': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )
