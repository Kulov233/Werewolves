# Generated by Django 5.1.3 on 2024-12-07 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_loses_userprofile_recent_games_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='games',
            field=models.JSONField(default=list, verbose_name='游戏记录'),
        ),
    ]
