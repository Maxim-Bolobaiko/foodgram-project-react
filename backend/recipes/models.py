from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    name = models.CharField("Название тега", unique=True, max_length=200)
    color = models.CharField(
        "Цветовой HEX-код",
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Введенное значение соответствует формату HEX!",
            )
        ],
    )
    slug = models.SlugField("Уникальный слаг", unique=True, max_length=200)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Название ингредиента", max_length=200)
    measurement_unit = models.CharField("Единицы измерения", max_length=200)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    name = models.CharField("Название рецепта", max_length=200)
    author = models.ForeignKey(
        User,
        related_name="recipe",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Автор рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name="recipe", verbose_name="Ингредиенты рецепта"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[MinValueValidator(1, message="Минимальное значение 1!")],
    )
    tag = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="Теги рецепта",
    )
    image = models.ImageField("Изображение", upload_to="recipes/")
    text = models.TextField("Описание рецепта")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент рецепта",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_in_recipe",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[MinValueValidator(1, message="Минимальное количество 1!")],
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"

    def __str__(self):
        return (
            f"{self.ingredient.name} ({self.ingredient.measurement_unit})"
            f" - {self.amount} "
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="unique_favourite"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзина покупок"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'
