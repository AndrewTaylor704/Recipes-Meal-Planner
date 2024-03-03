import scrapy
import pandas as pd
import numpy as np
import re

def test_string_contains(contents, testlist):
    if contents in testlist:
        testvar = True
    else:
        testvar = False
    return testvar

class RecipesSpider(scrapy.Spider):
    depth_param = 250
    name = "recipes"
    allowed_domains = ["bbcgoodfood.com"]
    start_urls = []
    for i in range(depth_param):
        start_urls.append("https://www.bbcgoodfood.com/search/?tab=recipe&mealType=dinner&sort=rating&page="+str(i+1))
    custom_settings = {"FEED_URI": "recipes.csv"}

    def parse(self, response):
        linkstr = '/recipes/'
        for href in response.css(".link.d-block::attr(href)").getall():
            if linkstr in href:
                recipe_page_link = response.urljoin(href)
                yield scrapy.Request(recipe_page_link, callback = self.parse_recipe)

    def parse_recipe(self, response):
        recipe_title = response.css('.heading-1::text').get().replace(',', '')
        recipe_url = response.request.url
        difficulty = response.css('.icon-with-text__children::text').getall()[0]
        try:
            serves = response.css('.icon-with-text__children::text').getall()[1]
        except:
            serves = "Serves 4"
        try:
            prep_time = response.css('.body-copy-small.list-item *::text').getall()[7]
            cook_time = response.css('.body-copy-small.list-item *::text').getall()[9]
            total_time = ""
        except:
            prep_time = ""
            cook_time = ""
            total_time = response.css('.body-copy-small.list-item *::text').getall()[7]
        categories = response.css('.terms-icons-list.d-flex.post-header__term-icons-list.mt-sm.hidden-print.list.list--horizontal *::text').getall()
        calories = response.css('.key-value-blocks__value::text').get()

        vegetarian = test_string_contains('Vegetarian', categories)
        healthy = test_string_contains('Healthy', categories)
        high_protein = test_string_contains('High-Protein', categories)
        low_calorie = test_string_contains('Low Calorie', categories)
        low_fat = test_string_contains('Low Fat', categories)
        freezable = test_string_contains('Freezable', categories)
        low_sugar = test_string_contains('Low Sugar', categories)
        gluten_free = test_string_contains('Gluten-free', categories)
        easily_doubled = test_string_contains('Easily doubled', categories)
        easily_halved = test_string_contains('Easily halved', categories)
        vegan = test_string_contains('Vegan', categories)
        high_fibre = test_string_contains('High-fibre', categories)
        dairy_free = test_string_contains('Dairy-free', categories)
        egg_free = test_string_contains('Egg-free', categories)
        keto = test_string_contains('Keto', categories)
        low_carb = test_string_contains('Low Carb', categories)

        rating_string = response.css('.sr-only *::text').getall()
        search_phrase = "A star rating of"
        rating = [s for s in rating_string if search_phrase in s][0]

        ingredient_list = []
        ingredient = response.css('.pb-xxs.pt-xxs.list-item.list-item--separator').getall()
        for idx in range(len(ingredient)):
            ingredient_string = re.sub('<[^<]+?>', '', ingredient[idx]).replace(',', '')
            ingredient_list.append(ingredient_string)

        method = " ".join(response.css('.pb-xs.pt-xs.list-item *::text').getall()).replace(',', '')

        scraped_recipe = {'title': recipe_title, 'difficulty': difficulty, 'calories' : calories, 'serves': serves, 'rating': rating, 'vegetarian': vegetarian, 'healthy': healthy, 
                            'high_protein': high_protein, 'low_calorie': low_calorie, 'low_fat': low_fat, 'freezable': freezable, 'low_sugar': low_sugar, 'gluten_free': gluten_free, 
                            'easily_doubled': easily_doubled, 'easily_halved': easily_halved, 'vegan': vegan, 'high_fibre': high_fibre, 'dairy_free': dairy_free, 'egg_free': egg_free, 
                            'keto': keto, 'low_carb': low_carb, 'prep_time': prep_time, 'cook_time': cook_time, 'total_time': total_time, 'method': method, 'recipe_url': recipe_url, 
                            'ingredient': ingredient_list}

        yield scraped_recipe