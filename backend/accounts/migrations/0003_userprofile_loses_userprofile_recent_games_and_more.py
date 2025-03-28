# Generated by Django 5.1.3 on 2024-12-06 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_avatar_alter_userprofile_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='loses',
            field=models.IntegerField(default=0, verbose_name='败场'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='recent_games',
            field=models.JSONField(default=list, verbose_name='最近三场游戏记录'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='wins',
            field=models.IntegerField(default=0, verbose_name='胜场'),
        ),
    ]
