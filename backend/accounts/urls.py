# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    # 注册视图
    path('register/', RegisterView.as_view(), name='register'),
    # 登录视图
    path('login/', LoginView.as_view(), name='login'),
    # 用户信息视图
    path('info/', UserInfoView.as_view(), name='info'),
    # 刷新视图，使用 refresh token 获取新的 access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 上传头像视图，仅能为JPG、PNG和GIF，最大 5 MB
    path('avatar/upload/', AvatarUploadView.as_view(), name='upload_avatar'),
    # 更新用户简介视图，最大 100 字符
    path('bio/update/', BioUpdateView.as_view(), name='update_bio'),
]
