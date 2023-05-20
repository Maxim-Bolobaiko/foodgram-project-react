from csv import reader

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open("data/ingredients.csv", encoding="utf-8") as ingredients:
            for row in reader(ingredients):
                if not Ingredient.objects.filter(
                    name=row[0],
                    measurement_unit=row[1],
                ).exists():
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
