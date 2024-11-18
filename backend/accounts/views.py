# accounts/views.py
from .serializers import RegisterSerializer, AvatarUploadSerializer, UserSerializer, BioUpdateSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *


# 注册
class RegisterView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问（包括未认证用户）

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "注册成功。"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 登录
class LoginView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问（包括未认证用户）

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = UsernameEmailLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data["user"]

            # 生成 JWT token
            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "登录成功。"
            }, status=status.HTTP_200_OK)
        except LoginError as e:
            return Response({e.param: e.message}, status=status.HTTP_401_UNAUTHORIZED)

# 获取用户信息
class UserInfoView(APIView):
    @staticmethod
    def get(request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

# 上传头像
class AvatarUploadView(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = AvatarUploadSerializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "头像上传成功。", "avatar_url": request.build_absolute_uri(user_profile.avatar.url)},
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 修改自我介绍
class BioUpdateView(APIView):
    @staticmethod
    def put(request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = BioUpdateSerializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "自我介绍修改成功。"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)