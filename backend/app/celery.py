# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认的 Django 配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# 创建 Celery 实例
app = Celery('app')

# 使用 Django 配置中的 Celery 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 用于 Celery 启动时加载配置的初始化代码
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
