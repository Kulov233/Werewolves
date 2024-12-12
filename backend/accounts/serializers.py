# accounts/serializers.py
import os

from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserProfile

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

    @staticmethod
    def validate_username(value):
        # 检查用户名是否已存在
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被注册。")
        return value

    @staticmethod
    def validate_email(value):
        # 检查邮箱是否已存在
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册。")
        return value

    def create(self, validated_data):
        # 创建新用户
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

# 用户个人资料序列化器
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'games']

# 用户公开信息序列化器
class PublicUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'wins', 'loses', 'recent_games']

# 用户个人信息序列化器
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

# 公开信息序列化器
class PublicInfoSerializer(serializers.ModelSerializer):
    profile = PublicUserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']

# 上传头像序列化器
class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(
        error_messages={
            'invalid_image': '请上传有效的图片文件。您上传的文件不是图片或是损坏的图片文件。',
            'empty': '请上传有效的图片文件。您上传的文件为空。',
            'invalid_extension': '请上传 JPEG、PNG 或 GIF 格式的图片文件。'
        }
    )

    class Meta:
        model = UserProfile
        fields = ['avatar']  # 只包含头像字段

    @staticmethod
    def validate_avatar(value):
        # 限制文件大小为5MB
        limit_kb = 5 * 1024
        if value.size > limit_kb * 1024:
            raise serializers.ValidationError(f"头像不能超过 {limit_kb / 1024} MB。")

        # 检查文件格式
        valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
        if value.content_type not in valid_mime_types:
            raise serializers.ValidationError("仅支持 JPEG、PNG 和 GIF 格式的头像。")

        return value

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance

# 修改自我介绍序列化器
class BioUpdateSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(
        max_length=100,
        allow_blank=True,
        error_messages={
            'max_length': '自我介绍不能超过100个字符。'
        }
    )

    class Meta:
        model = UserProfile
        fields = ['bio']

    def update(self, instance, validated_data):
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance
