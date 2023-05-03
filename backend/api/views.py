from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag, User
from rest_framework import filters, status, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = IsAuthenticatedOrReadOnly
    filter_backends = IngredientFilter
    search_fields = ("^name",)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = IsAuthenticatedOrReadOnly
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = IsAuthorOrReadOnly
    pagination_class = CustomPagination
    filter_backends = DjangoFilterBackend
    filterset_class = RecipeFilter


class UserViewSet(viewsets.ModelViewSet):
    pass
