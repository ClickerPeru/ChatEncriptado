from knox.models import AuthToken
from knox.settings import CONSTANTS


def get_user_from_token(token):
    objs = AuthToken.objects.filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH])
    if len(objs) == 0:
        return None
    return objs.first().user
