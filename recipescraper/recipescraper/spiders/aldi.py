import scrapy
import pandas as pd
import numpy as np
import re

class AldiSpider(scrapy.Spider):
    name = "aldi"
    allowed_domains = ["aldi.co.uk"]
    start_urls = []
    categories_list = ['vegan-range', 'bakery', 'fresh-food', 'drinks', 'food-cupboard', 
                        'frozen', 'chilled-food', 'baby-toddler', 'health-beauty', 'household', 'pet-care']


    for category in categories_list:
        start_urls.append(f'https://groceries.aldi.co.uk/en-GB/{category}')

    def parse(self, response):
        pass
#        linkstr = '/recipes/'
#        for href in response.css(".link.d-block::attr(href)").getall():
#            if linkstr in href:
#                recipe_page_link = response.urljoin(href)
#                yield scrapy.Request(recipe_page_link, callback = self.parse_recipe)

    def parse_shop(self, response):
#        recipe_title = response.css('.heading-1::text').get().replace(',', '')

#        scraped_data = {'title': recipe_title, 'difficulty': difficulty, 'calories'}
        pass
#        yield scraped_data