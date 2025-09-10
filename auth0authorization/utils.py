import json
import jwt
import requests
from django.contrib.auth import authenticate

from config import settings

def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://{}/.well-known/jwks.json'.format('dev-s6xqi0ox0fk82mwr.us.auth0.com')).json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = 'https://{}/'.format('dev-s6xqi0ox0fk82mwr.us.auth0.com')
    return jwt.decode(token, public_key, audience=settings.JWT_AUDIENCE, issuer=issuer, algorithms=['RS256'])

JWT_ISSUER = settings.JWT_AUTH['JWT_ISSUER']
JWT_AUDIENCE = settings.JWT_AUTH['JWT_AUDIENCE']


def jwt_get_username_from_payload_handler(payload):
    """
    Returns auth_id from jwt payload.
    """
    auth_id = payload.get('sub')
    return auth_id
