from django.contrib import admin
from django.apps import apps

# 需要排除的系统表（app_label,model_name）,注意前后单、复数
EXCLUDED_MODELS = [
    ('contenttypes', 'contenttype'),
    ('sessions', 'session'),
    ('migrations', 'migration'),
    ('auth', 'permission')
]


#自动注册所有未注册模型"
all_models = apps.get_models()
for model in all_models:
    if (model._meta.app_label, model._meta.model_name) in EXCLUDED_MODELS:
        continue
    elif model._meta.proxy:
        continue    # 跳过代理模型
    elif model in admin.site._registry:
        continue    # 跳过已注册模型
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
