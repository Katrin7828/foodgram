from rest_framework.pagination import PageNumberPagination

from .constants import DEFAULT_PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    """Пагинация."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
