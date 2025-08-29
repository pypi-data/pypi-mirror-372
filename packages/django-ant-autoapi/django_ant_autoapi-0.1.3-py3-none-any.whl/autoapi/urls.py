# urls.py（暴露 auto 路由）

from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView,)
from drf_spectacular.views import (SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView)
from rest_framework.permissions import AllowAny,IsAuthenticated


from .router import build_router

router = build_router()

urlpatterns = [
    # JWT 如单独给 token 保持匿名访问权限，则需添加 AllowAny
    path('token/', TokenObtainPairView.as_view(permission_classes=[AllowAny]), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=[AllowAny]), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(permission_classes=[AllowAny]), name='token_verify'),

    # OpenAPI Schema & 文档
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # 自动生成的 CRUD 路由
    path('v1/', include(router.urls)),
]