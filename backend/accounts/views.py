# accounts/views.py
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

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

# 获取用户个人信息
class UserInfoView(APIView):
    @staticmethod
    def get(request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

# 获取某个用户的公开信息
class PublicInfoView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问（包括未认证用户）

    @staticmethod
    def get(request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
        except Http404:
            return Response(
                {"message": "用户不存在。"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PublicInfoSerializer(user)
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
            return Response({
                "message": "自我介绍修改成功。",
                "bio": serializer.data["bio"]
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 获取某个ID的用户头像
class UserAvatarView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问（包括未认证用户）

    @staticmethod
    def get(request, user_id):
        # 获取用户头像
        try:
            user_profile = get_object_or_404(UserProfile, user__id=user_id)
        except Http404:
            return Response(
                {"message": "用户不存在。"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user_profile.avatar:
            # 重定向到头像 URL
            return Response(
                {"avatar_url": request.build_absolute_uri(user_profile.avatar.url)},
                status=status.HTTP_200_OK,
            )
        else:
            # 用户没有头像，返回 404 错误
            return Response(
                {"message": "该用户没有设置头像。"},
                status=status.HTTP_404_NOT_FOUND,
            )

# 获取好友列表
class FriendListView(APIView):
    @staticmethod
    def get(request):
        try:
            # 获取当前用户的profile
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)

            # 序列化数据
            serializer = FriendListSerializer(user_profile)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "message": "用户不存在。"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "message": "获取好友列表失败。"
            }, status=status.HTTP_400_BAD_REQUEST)

# 发送好友请求
class FriendAddView(APIView):
    @staticmethod
    def post(request):
        serializer = FriendRequestSendSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            target_id = serializer.validated_data['target']

            try:
                target_user = User.objects.get(id=target_id)

                if user == target_user:
                    return Response({
                        "status": "error",
                        "message": "不能添加自己为好友。"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 检查是否已经是好友
                if user_profile.friends.filter(id=target_id).exists():
                    return Response({
                        "status": "error",
                        "message": "已经是你的好友。"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 检查是否已经发送过请求
                if FriendRequest.objects.filter(
                        from_user=user,
                        to_user=target_user
                ).exists():
                    return Response({
                        "status": "error",
                        "message": "已经发送过好友请求。"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 检查是否已经收到过请求
                if FriendRequest.objects.filter(
                        from_user=target_user,
                        to_user=user
                ).exists():
                    return Response({
                        "status": "error",
                        "message": "对方已经发送过好友请求。"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 创建好友请求
                FriendRequest.objects.create(
                    from_user=user,
                    to_user=target_user
                )

                return Response({
                    "status": "success",
                    "message": "已发送好友请求。"
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "玩家不存在。"
                }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "error",
            "message": "请求格式错误。"
        }, status=status.HTTP_400_BAD_REQUEST)

# 处理好友请求
class FriendRequestView(APIView):
    @staticmethod
    def get(request):
        """获取收到的好友请求列表"""
        user_id = request.user.id
        friend_requests = FriendRequest.objects.filter(to_user_id=user_id)
        return Response({
            "player": user_id,
            "friend_requests": list(friend_requests.values_list('from_user_id', flat=True))
        }, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        """处理好友请求"""
        serializer = FriendRequestHandleSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            friend_request_id = serializer.validated_data['friend_request']
            try:
                friend_request = FriendRequest.objects.get(
                    to_user=request.user,
                    from_user_id=friend_request_id
                )
            except FriendRequest.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "好友请求不存在。"
                }, status=status.HTTP_404_NOT_FOUND)

            if serializer.validated_data['type'] == 'accept':
                friend_request.accept()
                return Response({
                    "status": "success",
                    "message": "已接受好友请求。"
                }, status=status.HTTP_200_OK)
            else:  # deny
                friend_request.reject()
                return Response({
                    "status": "success",
                    "message": "已拒绝好友请求。"
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 删除好友
class FriendDeleteView(APIView):
    @staticmethod
    def post(request):
        serializer = FriendDeleteSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            target_id = serializer.validated_data['target']

            try:
                # 双向删除好友关系
                user.userprofile.friends.remove(target_id)
                target_user = User.objects.get(id=target_id)
                target_user.userprofile.friends.remove(user.id)

                return Response({
                    "message": "好友删除成功。"
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({
                    "message": "用户不存在。"
                }, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 搜索用户
class UserSearchView(APIView):
    @staticmethod
    def get(request):
        user_id = request.user.id
        keyword = request.GET.get('keyword', '')
        if not keyword:
            return Response({
                "message": "请输入搜索关键词。"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 使用 Q 对象组合查询条件
        from django.db.models import Q
        users = User.objects.filter(
            Q(username__icontains=keyword) |  # 用户名包含关键词（不区分大小写）
            Q(id__iexact=keyword)  # ID 完全匹配
        ).exclude(id=user_id
        ).values('id', 'username')[:10]  # 限制返回数量

        return Response({
            "users": list(users)
        }, status=status.HTTP_200_OK)

# 修改密码
class PasswordChangeView(APIView):
    @staticmethod
    def post(request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            # 修改密码
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()

            return Response({
                "message": "密码修改成功。"
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)