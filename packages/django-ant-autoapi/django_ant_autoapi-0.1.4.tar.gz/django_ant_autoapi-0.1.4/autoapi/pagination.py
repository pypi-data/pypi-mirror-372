# pagination.py（可选，统一页大小参数）

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size_query_param = 'page_size' # 允许客户端动态设置每页数量,如果不传 page_size参数，则使用全局默认值（需在 settings.py中设置 PAGE_SIZE）
    max_page_size = 500                 # 每页最大数据量限制
