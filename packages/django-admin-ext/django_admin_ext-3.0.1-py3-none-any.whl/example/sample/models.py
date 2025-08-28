from django.db import models


class FoodType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    food_type = models.ManyToManyField(FoodType)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class IngredientDetails(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Meal(models.Model):
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE)
    main_ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    ingredient_details = models.ForeignKey(IngredientDetails, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.food_type, self.main_ingredient)
