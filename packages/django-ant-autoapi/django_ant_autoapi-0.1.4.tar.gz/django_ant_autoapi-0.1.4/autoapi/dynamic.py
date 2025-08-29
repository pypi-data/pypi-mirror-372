# dynamic.py（动态 Serializer & ViewSet 工厂）

from typing import Dict, Any
from django.apps import apps as django_apps
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets, filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .pagination import DefaultPagination
from .permissions import DefaultPermission


# 需要排除的系统表（app_label,model_name）,注意前后单、复数
EXCLUDED_MODELS = [
    ('contenttypes', 'contenttype'),
    ('sessions', 'session'),
    ('migrations', 'migration'),
    ('auth', 'permission')
]

# 排除指定modes中的敏感字段
SENSITIVE_FIELDS = {
    "User": ["password", "last_login","username",],   # User 模型要排除的字段
    # "LogEntry": ["change_message"],
}


# ------- 读取模型上的 ApiMeta 轻量配置 -------

def read_api_meta(model) -> Dict[str, Any]:
    Meta = getattr(model, 'ApiMeta', None)
    cfg = {
        'fields': '__all__',
        'read_only': ('id',),
        'depth': 0,
        'search_fields': (),
        'ordering_fields': (),
        'filterset_fields': (),
        'lookup_field': 'pk',
        'permission_classes': None,
        'basename': None,
        'public': True,
        'tags': (model._meta.app_label,),
        'user_field': None,
    }
    if Meta:
        for k in cfg.keys():
            if hasattr(Meta, k):
                cfg[k] = getattr(Meta, k)
    return cfg


# ------- 动态创建 Serializer -------

def build_serializer(model, cfg) -> serializers.ModelSerializer:
    meta_attrs = {
        'model': model,
        'fields': cfg['fields'],
        'read_only_fields': cfg['read_only'],
    }
    if cfg.get('depth'):
        meta_attrs['depth'] = cfg['depth']

    MetaCls = type('Meta', (), meta_attrs)

    sensitive_fields = SENSITIVE_FIELDS.get(model.__name__, [])

    serializer_name = f"{model._meta.app_label}_{model.__name__}AutoSerializer" # 确保唯一类名
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        for field in sensitive_fields:
            self.fields.pop(field, None)

    serializer_cls = type(
        serializer_name,
        (serializers.ModelSerializer,),
        {'Meta': MetaCls, '__init__': __init__}
    )

    return serializer_cls


# ------- 公共基类 ViewSet -------

class BaseAutoModelViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    pagination_class = DefaultPagination
    ordering = ['-id']


# ------- 动态创建 ViewSet -------

def build_viewset(model, serializer_cls, cfg):
    attrs = {
        'queryset': model.objects.all(),
        'serializer_class': serializer_cls,
        'lookup_field': cfg['lookup_field'],
        '__doc__': f'Auto CRUD for {model._meta.label}',
    }

    # 添加搜索、排序、过滤、权限
    if cfg.get('search_fields'):
        attrs['search_fields'] = cfg['search_fields']
    if cfg.get('ordering_fields'):
        attrs['ordering_fields'] = cfg['ordering_fields']
    if cfg.get('filterset_fields'):
        attrs['filterset_fields'] = cfg['filterset_fields']
    if cfg.get('permission_classes'):
        attrs['permission_classes'] = cfg['permission_classes']

    # admin_log → 只读
    if model == LogEntry:
        base_cls = viewsets.ReadOnlyModelViewSet
        extra_attrs = {'http_method_names': ['get', 'head', 'options']}
    else:
        base_cls = BaseAutoModelViewSet
        extra_attrs = {}

    # ---------- 动态生成 ViewSet 内部类 ----------
    class AutoViewSet(base_cls):
        queryset = model.objects.all()
        serializer_class = serializer_cls
        lookup_field = cfg['lookup_field']

        def get_queryset(self):
            user = self.request.user
            qs = super().get_queryset()

            # ---------- 模型级权限检查 ----------
            if model != get_user_model():   # 用户模型不需要权限检查
                perm_codename = f'view_{model._meta.model_name}'
                if not user.has_perm(f'{model._meta.app_label}.{perm_codename}'):
                    return model.objects.none()  # 没权限返回空

            # ---------- 普通用户只能看自己 ----------
            if not user.is_staff:
                if model == get_user_model():
                    qs = qs.filter(pk=user.pk)
                # 其他模型按照 ApiMeta.user_field 指定字段过滤行级数据
                else:
                    user_field = getattr(cfg, 'user_field', None)
                    if user_field and hasattr(model, user_field):
                        qs = qs.filter(**{user_field: user})
            return qs

    # 👈 合并额外属性（如 admin_log 的 http_method_names）
    for k, v in extra_attrs.items():
        setattr(AutoViewSet, k, v)

    # ---------- 确保类名唯一，避免 schema 冲突 ----------
    AutoViewSet.__name__ = f'{model.__name__}AutoViewSet'
    serializer_cls.__name__ = f'{model.__name__}AutoSerializer'

    # ---------- 为文档打标签 ----------
    AutoViewSet = extend_schema(tags=list(cfg.get('tags') or []))(AutoViewSet)

    return AutoViewSet

# ------- 枚举所有模型（跳过代理与自动创建的中间表） -------

def iter_concrete_models():
    for model in django_apps.get_models():
        opts = model._meta
        if opts.proxy:
            continue    # 排除代理模型
        if opts.auto_created:  # 通常是多对多中间表
            continue
        if (opts.app_label, opts.model_name) in EXCLUDED_MODELS:
            continue
        yield model