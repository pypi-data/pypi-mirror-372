from .api_serializers import PaperSerializer
from rest_framework import viewsets
from .api_serializers import PaperSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter

from .models import Paper

class PaperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows access to paper data.
    """
    queryset = Paper.objects.all().order_by('-year')
    serializer_class = PaperSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = (
        'title',
        'authors__id',
        'authors__lastname',
        'authors__firstname',
        'authors__user__username',
        'tags__value',
        'keywords__name',
        'year', )
