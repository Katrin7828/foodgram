from rest_framework.pagination import PageNumberPagination


SIZE = 6


class FoodgramPagination(PageNumberPagination):
    """Пагинация."""

    page_size = SIZE
    page_size_query_param = 'limit'
