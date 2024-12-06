from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import os

from django.db.models import JSONField


# 将用户上传的头像重命名为用户的 ID
def user_directory_path(instance, filename):
    # 获取文件的扩展名
    _, ext = os.path.splitext(filename)
    # 将文件名设置为用户的 ID
    filename = f"{instance.user.id}{ext}"
    # 指定文件的上传目录为 avatars/
    path = os.path.join('avatars', filename)
    # 检测文件名是否已存在
    if os.path.exists(os.path.join('media', path)):
        os.remove(os.path.join('media', path)) # TODO: 如果用户上传了以不同扩展名的同名文件，原有文件不会被删除，不过这个问题不大
    return path

# 扩展的用户模型
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField("自我介绍", max_length=500, blank=True, default="这个人很懒，还没有自我介绍~")  # 自我介绍字段
    # TODO: 可能的前端bug：头像可能为null
    avatar = models.ImageField("头像", upload_to=user_directory_path, null=True)  # 头像字段
    """
    {
        "date": "2024-12-6",
        "won": true
    }
    """
    recent_games = JSONField("最近三场游戏记录", default=list)  # 最近三场游戏记录
    wins = models.IntegerField("胜场", default=0)  # 胜场
    loses = models.IntegerField("败场", default=0)  # 败场

    def __str__(self):
        return self.user.username