from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Base64ImageField, SerializerMethodField
from rest_framework.serializers import PrimaryKeyRelatedField
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class FollowingSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes_count", "recipes")
        read_only_fields = ("first_name", "last_name", "username", "email")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = Ingredient
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
    is_in_favorite = serializers.SerializerMethodField()
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
            "is_in_favorite",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_in_favorite(self, obj):
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
    ingredients = IngredientInRecipeSerializer(many=True)
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
        ingredients_list = []
        if not ingredients:
            raise ValidationError("Нужно выбрать хотя бы один ингредиент!")
        for ingredient in ingredients:
            if ingredient["id"] in ingredients_list:
                raise ValidationError("Ингридиенты должны быть уникальными!")
            if int(ingredient.get("amount")) < 1:
                raise ValidationError(
                    "Количество ингредиента должно быть больше 0!"
                )
            ingredients_list.append(ingredient)
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

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                IngredientInRecipe(
                    ingredient=ingredient.pop("id"),
                    amount=ingredient.pop("amount"),
                    recipe=recipe,
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        request = self.context.get("request", None)
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop("tags"))
        ingredients = validated_data.pop("ingredients")
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time", "image")


class FavoriteSerializer(serializers.ModelSerializer):
    pass


class ShoppingCartSerializer(serializers.ModelSerializer):
    pass
