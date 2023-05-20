from django.db.models import Sum

from recipes.models import IngredientInRecipe


def get_shopping_list(user):
    ingredients = (
        IngredientInRecipe.objects.filter(recipe__shopping_cart__user=user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(amount=Sum("amount"))
    )

    shopping_list = "Список покупок:"
    for ingredient in ingredients:
        shopping_list += (
            f"\n{ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}) - "
            f"{ingredient['amount']}"
        )

    return shopping_list
