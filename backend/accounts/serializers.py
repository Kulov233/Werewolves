# accounts/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate

# 注册序列化器
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        error_messages={
            'blank': '用户名不能为空。',
            'max_length': '用户名不能超过150个字符。'
        }
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'blank': '密码不能为空。',
            'min_length': '密码不能少于8个字符。'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': '邮箱不能为空。',
            'invalid': '邮箱格式错误。'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email')
        )
        return user

class LoginError(Exception):
    def __init__(self, param, message):
        self.param = param
        self.message = message

# 用户名或邮箱登录序列化器，支持用户名和邮箱登录
class UsernameEmailLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(allow_blank=True)
    password = serializers.CharField(write_only=True, allow_blank=True)

    def validate(self, data):
        username_or_email = data.get("username_or_email")
        password = data.get("password")

        # 检查是否是邮箱格式
        if "@" in username_or_email:
            # 尝试用邮箱查找用户
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                raise LoginError("username_or_email", "用户不存在。")
        else:
            username = username_or_email
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise LoginError("username_or_email", "用户不存在。")

        # 使用用户名进行认证
        user = authenticate(username=username, password=password)
        if user is None:
            raise LoginError("password", "密码错误。")

        data["user"] = user
        return data
