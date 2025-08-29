# permissions.py（可选,权限控制）

from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated

# 这里先复用 DRF 的权限。若需要更细粒度，可自定义新类。
DefaultPermission = IsAuthenticated