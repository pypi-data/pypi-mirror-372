'''
可以在任何模型中加一个内部类 ApiMeta，用于微调这个模型对应 API 的行为。
不配置 ApiMeta 也没问题，系统会采用合理的默认值。
示例：autoapi/models.py/Profile
'''

from django.db import models
from django.conf import settings

# 调整 models 的重要示例，参考 ApiMeta，建议保留
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auto_profile')
    display_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    class ApiMeta:
        fields = '__all__'                  # 或明确列出字段
        read_only = ('id', 'created_at', 'updated_at')
        depth = 0                           # 关系展开层级（谨慎调大）
        search_fields = ('display_name', 'user__username')
        ordering_fields = ('id', 'created_at')
        filterset_fields = ('user',)
        lookup_field = 'pk'                 # 或 'id' / 'uuid' / 'slug'
        public = True                       # False 表示不对外暴露该模型 API
        tags = ('AutoApi',)                 # 文档标签
        # user_field = 'user'                 # 用户字段，用于权限控制用户行数据
        # permission_classes = [CustomPermission]  # 如需单独权限

    def __str__(self):
        return self.display_name