# __init__.py

from __future__ import absolute_import, unicode_literals

# 使得 Celery 能在 Django 启动时自动加载
from .celery import app as celery_app

__all__ = ('celery_app',)
