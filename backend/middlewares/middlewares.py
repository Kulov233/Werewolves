# middlewares.py
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async


from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

@database_sync_to_async
def get_user_from_token(token):
    try:
        # 验证 JWT 令牌并解码
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        User = get_user_model()
        return User.objects.get(id=user_id)
    except Exception:
        from django.contrib.auth.models import AnonymousUser
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 从查询字符串中获取 token
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            from django.contrib.auth.models import AnonymousUser
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
