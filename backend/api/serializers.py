from recipes.models import Ingredient, Recipe, Tag
from rest_framework import serializers
from users.models import Following, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeReadSerializer(serializers.ModelSerializer):
    pass


class RecipeCreateSerializer(serializers.ModelSerializer):
    pass


class FavoriteSerializer(serializers.ModelSerializer):
    pass


class ShoppingCartSerializer(serializers.ModelSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    pass


class SubscribeSerializer(serializers.ModelSerializer):
    pass
