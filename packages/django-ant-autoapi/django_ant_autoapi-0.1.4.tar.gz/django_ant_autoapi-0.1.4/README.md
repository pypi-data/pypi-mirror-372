一、项目结构
django-ant-autoapi/
├── autoapi/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── dynamic.py
│   ├── admin.py
│   ├── urls.py
│   ├── router.py
│   └── migrations/
├── setup.py
├── pyproject.toml
├── MANIFEST.in
├── README.md
└── LICENSE


二、简介（Summary）

简介（Summary）

django-ant-autoapi 是一个基于 Django REST Framework (DRF) 的自动化 CRUD 与接口文档生成工具。
零配置即可自动扫描 Django 模型并自动生成完整 REST API、Serializer、ViewSet、路由和 Swagger/Redoc 文档。
内置 JWT 认证、权限控制、敏感字段隐藏、搜索、过滤、排序和分页功能。
自动注册模型到 Django Admin，帮助开发者快速构建管理后台、原型系统或内部 API，让你专注业务逻辑而无需重复写 CRUD 代码。
后端框架基于Python3.13与django5.2.5

	•	⚡ 零配置：安装即可使用，自动扫描模型生成 API。
	•	🔑 自动注册：支持自动生成 Serializer、ViewSet、路由和 Swagger / Redoc 文档。
	•	🔒 内置安全：JWT 认证、权限控制，敏感字段（如密码、密钥）自动隐藏。
	•	🌐 CORS 支持：开发环境默认允许所有来源，可配置。
	•	🔍 强大查询：搜索、过滤、排序、分页一应俱全。
	•	🛠 可扩展：通过模型内部 ApiMeta 轻松微调字段、权限、搜索等。
	•	🛡️ Admin 集成：自动注册模型到 Django 自带 Admin，方便调试。


🚀 特性
	•	⚡ 零配置：安装即可使用，用户只需要专注写 models。
	•	🔄 自动扫描 `INSTALLED_APPS` 中所有启用App,并自动生成 DRF CRUD API 、序列化器和接口文档。
	•	🔑 内置 JWT 认证与权限控制
	•	🔒 敏感字段自动隐藏（如密码、密钥）
	•	🌐 跨域支持（CORS），DEBUG模式默认允许所有来源，可在 apps.py 中自定义规则。
	•	📑 基于 drf-spectacular 自动生成 Swagger UI & Redoc API文档。
	•	🔍 搜索、过滤、排序、分页
	•	🛠 可通过模型内部 ApiMeta 进行深度定制
	•	🛡️ 自动注册到 Django Admin，方便调试。
	•	🗂️ 提供增删改查、筛选、全量导出、选择导出等功能
	•	🔐 支持 Django 自带权限系统


=========================================================================

三、快速使用
1.下载完整项目并安装相关依赖
git clone https://github.com/buslink/Django-Ant-Admin
cd Django-Ant-Admin
pip install -r requirements.txt

2.已有Django 项目中使用

pip install django-ant-autoapi
# (安装requirements.txt)
pip install -r requirements.txt

在 settings.py 中添加：

INSTALLED_APPS = [
    # 业务 app
    'autoapi',

    #第三方模块
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'corsheaders',
    'django_filters',
]


在 urls.py 中添加：

urlpatterns = [
    ...
    # + api路由入口
    path('api/', include('autoapi.urls')),
]


其他配置
	•模型内部可定义 ApiMeta 来微调字段、搜索、排序、权限等（参考 autoapi/models.py 示例）。
	•默认敏感字段通过autoapi/dynamic.py SENSITIVE_FIELDS 自动隐藏。


3.初始化后端

<!-- 自定义 model后，生成库表 -->
<!-- autoapi.models.Profile model权限调整示例 -->

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser    # 创建管理员
python manage.py runserver

http://127.0.0.1:8000/admin         # django自带管理后台
http://127.0.0.1:8000/api/token/    # 获取 JWT token
http://127.0.0.1:8000/api/docs/     # Swagger UI 接口文档
http://127.0.0.1:8000/api/redoc/    # Redoc 接口文档


4.初始化前端
安装 node.js，直接调用 /api/v1/<ModelName>/ 的接口即可，无需额外配置。


交流
QQ群：1047231652