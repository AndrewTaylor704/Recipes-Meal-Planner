import pandas as pd
import numpy as np

random_seed = 12345678
rng = np.random.default_rng(seed = random_seed)

recipe_file_path = 'C:/Users/aglt7/projects/Recipes Meal Planner/recipescraper/recipes.csv'

recipes = pd.read_csv(recipe_file_path)
max_recipes = int(recipes.shape[0])

def random_recipe(num_recipes):
    recipe_list = []
    for i in range(num_recipes):
        rand_idx = rng.integers(max_recipes)
        recipe_list.append(recipes.loc[rand_idx])
    return pd.DataFrame(recipe_list)

recipe_list = random_recipe(5)
print(recipe_list[['title', 'calories', 'recipe_url']])