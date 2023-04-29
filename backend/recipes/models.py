from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

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
        "Автор рецепта",
        User,
        related_name="recipe",
        on_delete=models.CASCADE,
        null=True,
    )
    ingredients = models.ManyToManyField(
        "Ингредиенты рецепта", Ingredient, related_name="recipe"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[MinValueValidator(1, message="Минимальное значение 1!")],
    )
    tag = models.ManyToManyField("Теги рецепта", Tag, related_name="recipe")
    image = models.ImageField("Изображение", upload_to="recipes/")
    text = models.TextField("Описание рецепта")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name
