# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    # 注册视图
    path('register/', RegisterView.as_view(), name='register'),
    # 登录视图
    path('login/', LoginView.as_view(), name='login'),
    # 用户个人信息视图
    path('info/', UserInfoView.as_view(), name='info'),
    # 刷新视图，使用 refresh token 获取新的 access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 获取某个用户公开信息视图
    path('public_info/<int:user_id>/', PublicInfoView.as_view(), name='public_info'),
    # 获取头像视图，获取ID为所给ID的用户的头像
    path('avatar/<int:user_id>/', UserAvatarView.as_view(), name='get_avatar'),
    # 上传头像视图，仅能为JPG、PNG和GIF，最大 5 MB
    path('avatar/upload/', AvatarUploadView.as_view(), name='upload_avatar'),
    # 更新用户简介视图，最大 100 字符
    path('bio/update/', BioUpdateView.as_view(), name='update_bio'),
    # 获取好友列表
    path('friends/list/', FriendListView.as_view(), name='friend-list'),
    # 发送好友请求
    path('friends/add/', FriendAddView.as_view(), name='friend-add'),
    # 处理好友请求
    path('friends/requests/', FriendRequestView.as_view(), name='friend-requests'),
    # 删除好友
    path('friends/delete/', FriendDeleteView.as_view(), name='friend-delete'),
    # 搜索用户
    path('search/', UserSearchView.as_view(), name='user-search'),
    # 修改密码
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
]
