from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import PrimaryKeyRelatedField

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Following, User


class UserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Following.objects.filter(follower=user, following=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password")


class FollowingSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes_count", "recipes")
        read_only_fields = ("first_name", "last_name", "username", "email")

    def validate(self, data):
        follower = self.context.get("request").user
        following_id = (
            self.context.get("request").parser_context.get("kwargs").get("id")
        )
        following = get_object_or_404(User, id=following_id)

        if Following.objects.filter(
            follower=follower, following=following
        ).exists():
            raise ValidationError(
                detail="Вы уже подписались!", code=status.HTTP_400_BAD_REQUEST
            )
        if follower == following:
            raise ValidationError(
                detail="Вы не можете подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipe.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipe.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source="ingredient_in_recipe"
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "author",
            "ingredients",
            "cooking_time",
            "tags",
            "image",
            "text",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredient_in_recipe.all()
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True, unique=True)
    cooking_time = serializers.IntegerField()
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "author",
            "ingredients",
            "cooking_time",
            "tags",
            "image",
            "text",
        )

    def validate_ingredients(self, ingredients):
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError(
                "Нужно выбрать хотя бы один ингредиент!"
            )
        for ingredient in ingredients:
            ingredient_id = ingredient["ingredient"]["id"]
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(
                    {"ingredient": "Ингредиенты должны быть уникальными!"}
                )
            if int(ingredient.get("amount")) < 1:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть больше 0!"
                )
            ingredients_set.add(ingredient_id)
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise ValidationError(
                "Время готовки должно быть не меньше одной минуты!"
            )
        return cooking_time

    def validate_tags(self, tags):
        tags_list = []
        if not tags:
            raise ValidationError("Нужно выбрать хотя бы один тег!")
        for tag in tags:
            if tag in tags_list:
                raise ValidationError("Теги должны быть уникальными!")
            tags_list.append(tag)
        return tags

    def create_ingredients(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient=Ingredient.objects.get(
                        id=ingredient["ingredient"]["id"]
                    ),
                    recipe=recipe,
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        request = self.context.get("request", None)
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        instance = super().update(instance, validated_data)

        instance.tags.clear()
        instance.ingredients.clear()

        instance.tags.set(tags)
        self.create_ingredients(recipe=instance, ingredients=ingredients)

        instance.save()

        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time", "image")


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            "user",
            "recipe",
        )

    def validate(self, data):
        user = data["user"]
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise ValidationError("Рецепт уже добавлен в избранное!")
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            "user",
            "recipe",
        )

    def validate(self, data):
        user = data["user"]
        if user.shopping_cart.filter(recipe=data["recipe"]).exists():
            raise ValidationError("Рецепт уже добавлен в корзину")
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data
