from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 3
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "recipe_in_favorite",
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    search_fields = (
        "name",
        "author__username",
        "tags__name",
    )
    inlines = (IngredientInline,)

    def recipe_in_favorite(self, obj):
        return obj.favorites.count()

    recipe_in_favorite.short_description = "Добавлений в избранное"


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "recipe",
        "amount",
    )


@admin.register(Favorite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
