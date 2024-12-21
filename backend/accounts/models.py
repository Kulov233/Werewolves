from datetime import datetime

from django.contrib.auth.models import User
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

# 好友请求模型
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def accept(self):
        # 添加好友关系
        from_user_profile, created = UserProfile.objects.get_or_create(user=self.from_user)
        to_user_profile, created = UserProfile.objects.get_or_create(user=self.to_user)
        from_user_profile.friends.add(self.to_user)
        to_user_profile.friends.add(self.from_user)
        # 删除请求
        self.delete()

    def reject(self):
        # 直接删除请求
        self.delete()

# 扩展的用户模型
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField("自我介绍", max_length=500, blank=True, default="这个人很懒，还没有自我介绍~")  # 自我介绍字段
    # TODO: 可能的前端bug：头像可能为null
    avatar = models.ImageField("头像", upload_to=user_directory_path, null=True, default="avatars/default.png")  # 头像字段

    """
    {
        "date": "2024-12-6",
        "won": true
    }
    """
    recent_games = JSONField("最近三场游戏记录", default=list)  # 最近三场游戏记录，公开

    """
    {
        "role": "Villager",
        "date": "2024-12-6",
        "duration": 2, [分钟]
        "won": true
    }
    """
    games = JSONField("游戏记录", default=list)  # 游戏记录，私密
    wins = models.IntegerField("胜场", default=0)  # 胜场，公开
    loses = models.IntegerField("败场", default=0)  # 败场，公开

    friends = models.ManyToManyField(User, related_name='friend_of', blank=True)  # 好友列表，私密

    def __str__(self):
        return self.user.username

    def add_game_record(self, started_at: str, won: bool, role: str):
        """添加游戏记录"""
        # 最近三场游戏记录
        if not isinstance(self.recent_games, list):
            self.recent_games = []

        new_record = {
            "date": datetime.now().isoformat(),
            "won": won
        }

        self.recent_games.append(new_record)
        self.recent_games = self.recent_games[-3:]  # 保持最新的3条

        # 胜败场次
        if won:
            self.wins += 1
        else:
            self.loses += 1

        # 游戏记录
        if not isinstance(self.games, list):
            self.games = []

        started_at_datetime = datetime.fromisoformat(started_at)
        # 持续时间，单位：分钟
        duration = int((datetime.now() - started_at_datetime).total_seconds() / 60)

        new_record_detailed = {
            "role": role,
            "date": datetime.now().isoformat(),
            "duration": duration,
            "won": won
        }

        self.games.append(new_record_detailed)

        self.save()

    def remove_friend(self, friend_user):
        if friend_user in self.friends.all():
            self.friends.remove(friend_user)

    def get_friend_ids(self) -> list[int]:
        """获取好友ID列表（整数形式）"""
        return list(self.friends.values_list('id', flat=True))