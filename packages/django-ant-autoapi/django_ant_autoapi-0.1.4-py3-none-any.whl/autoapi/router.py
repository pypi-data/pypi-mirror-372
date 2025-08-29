# router.py（自动注册所有模型的路由）

from rest_framework.routers import DefaultRouter
from .dynamic import iter_concrete_models, read_api_meta, build_serializer, build_viewset


def build_router() -> DefaultRouter:
    router = DefaultRouter()

    for model in iter_concrete_models():
        cfg = read_api_meta(model)
        if not cfg.get('public', True):
            continue  # 模型显式不公开

        serializer_cls = build_serializer(model, cfg)
        viewset_cls = build_viewset(model, serializer_cls, cfg)

        # 为了避免跨 app 的重名模型冲突，使用 app_label/model_name 作为前缀
        prefix = f"{model._meta.app_label}/{model._meta.model_name}"
        basename = cfg.get('basename') or f"{model._meta.app_label}-{model._meta.model_name}"
        router.register(prefix, viewset_cls, basename=basename)

    return router