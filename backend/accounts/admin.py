from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')  # 在管理后台显示的字段

# Register your models here.
admin.site.register(UserProfile)