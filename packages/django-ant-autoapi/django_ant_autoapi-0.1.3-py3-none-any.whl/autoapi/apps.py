from django.apps import AppConfig
from django.conf import settings


class AutoApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'autoapi'

    def ready(self):
        # ==== 1. 自动注入 CORS 中间件 ====
        cors_middleware = "corsheaders.middleware.CorsMiddleware"
        if hasattr(settings, "MIDDLEWARE") and cors_middleware not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.insert(0, cors_middleware)

        # ==== 2. 自动注入 CORS 配置 ====
        if getattr(settings, "DEBUG", False):
            # 开发模式：允许所有
            settings.CORS_ALLOW_ALL_ORIGINS = True
        else:
            # 生产模式：限制 localhost / 127.0.0.1
            if not hasattr(settings, "CORS_ALLOW_ALL_ORIGINS"):
                settings.CORS_ALLOW_ALL_ORIGINS = False
            if not hasattr(settings, "CORS_ALLOWED_ORIGIN_REGEXES"):
                settings.CORS_ALLOWED_ORIGIN_REGEXES = [
                    r"^http?:\/\/localhost(:\d+)?$",
                    r"^http?:\/\/127\.0\.0\.1(:\d+)?$",
                ]

        # ==== 3. 自动注入 REST_FRAMEWORK 配置 ====
        rest_default = {
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_PERMISSION_CLASSES': (
                'rest_framework.permissions.IsAuthenticated',
            ),
            'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
            'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
            'PAGE_SIZE': 20,
            'DEFAULT_FILTER_BACKENDS': (
                'django_filters.rest_framework.DjangoFilterBackend',
                'rest_framework.filters.SearchFilter',
                'rest_framework.filters.OrderingFilter',
            ),
        }
        if not hasattr(settings, "REST_FRAMEWORK"):
            settings.REST_FRAMEWORK = {}
        for key, val in rest_default.items():
            settings.REST_FRAMEWORK.setdefault(key, val)

        # ==== 4. 自动注入 SIMPLE_JWT 配置 ====
        from datetime import timedelta
        jwt_default = {
            'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
            'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
            'ROTATE_REFRESH_TOKENS': True,
            'BLACKLIST_AFTER_ROTATION': True,
            'COOKIE_HTTPONLY': True,
            # 'COOKIE_SECURE': True,  # 仅HTTPS传输
            'COOKIE_SAMESITE': 'Lax',
        }
        if not hasattr(settings, "SIMPLE_JWT"):
            settings.SIMPLE_JWT = {}
        for key, val in jwt_default.items():
            settings.SIMPLE_JWT.setdefault(key, val)

        # ==== 5. 自动注入 drf-spectacular 配置 ====
        spectacular_default = {
            'TITLE': 'Djano_Ant_Admin API',
            'DESCRIPTION': '基于 DRF 的自动化 CRUD 与接口文档生成',
            'VERSION': '1.3.6',
            'COMPONENT_SPLIT_REQUEST': True,
            'SCHEMA_PATH_PREFIX': r'/api/v1',
            'SWAGGER_UI_SETTINGS': {
                'persistAuthorization': True,
            },
            "SERVE_INCLUDE_SCHEMA": True if getattr(settings, "DEBUG", True) else False,
            'SERVE_PERMISSIONS': [] if getattr(settings, "DEBUG", True) else ['rest_framework.permissions.IsAuthenticated'],
            "SERVE_AUTHENTICATION": [] if getattr(settings, "DEBUG", True) else ["rest_framework_simplejwt.authentication.JWTAuthentication"],
            'SECURITY': [{'BearerAuth': []}],
            'COMPONENTS': {
                'securitySchemes': {
                    'BearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT',
                    }
                }
            },
        }
        if not hasattr(settings, "SPECTACULAR_SETTINGS"):
            settings.SPECTACULAR_SETTINGS = {}
        for key, val in spectacular_default.items():
            settings.SPECTACULAR_SETTINGS.setdefault(key, val)