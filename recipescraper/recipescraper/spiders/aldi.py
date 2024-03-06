import scrapy
import pandas as pd
import numpy as np
import re
import time
from scrapy_selenium import SeleniumRequest
import requests

class AldiSpider(scrapy.Spider):
    name = "aldi"
    allowed_domains = ["aldi.co.uk"]
    custom_settings = {"FEED_URI": "aldi.csv"}

    def start_requests(self):
        categories_list = ['vegan-range', 'bakery', 'fresh-food', 'drinks', 'food-cupboard', 
                            'frozen', 'chilled-food', 'baby-toddler', 'health-beauty', 'household', 'pet-care']
        for category in categories_list:
            url = f'https://groceries.aldi.co.uk/en-GB/{category}?&page=1'
            yield SeleniumRequest(url=url, callback=self.parse, meta={'category':category})

    def parse(self, response):
        last_page_number = int(response.css('.pagination-dropdown::attr(data-pages)').get())
        product_raw_data = response.css('.products-search-results::attr(data-context)').get()
        next_page_number = int(re.findall(r'(?<="PaginationCurrentPage":{"DisplayName":")[\d]+', product_raw_data)[0]) + 1
        print(next_page_number)
        product_name, product_price, product_url, product_size, product_id = self.parse_raw_data(product_raw_data)
        category = response.meta['category']
        scraped_data = {}
        for idx, _ in enumerate(product_name):
            scraped_data = {'product_name': product_name[idx], 'product_price': product_price[idx], 
                            'product_url': product_url[idx], 'product_size':product_size[idx], 
                            'product_id':product_id[idx], 'category':category, 'page_number':next_page_number - 1}
            yield scraped_data
        
        if next_page_number <= last_page_number:
            url = f'https://groceries.aldi.co.uk/en-GB/{category}?&page={next_page_number}'
            yield SeleniumRequest(url=url, callback=self.parse, meta={'category':category})

    def parse_raw_data(self, product_raw_data):
        product_name = re.findall(r'(?<="FullDisplayName":")(.*?)(?=")', product_raw_data)
#       product_price = re.findall(r'(?<="ListPrice":)[\d]+\.[\d]+', product_raw_data)
        product_url = re.findall(r'(?<=[^{]"Url":")[\w\s/-]+', product_raw_data)
        product_size = re.findall(r'(?<="SizeVolume":")[\w\s]+', product_raw_data)
        product_id = re.findall(r'(?<="ProductId":")[\d]+', product_raw_data)
        product_price = self.get_correct_prices(product_id)

        for idx, input_str in enumerate(product_name):
            product_name[idx] = self.remove_spec_chars(input_str)

        for idx, url in enumerate(product_url):
            product_url[idx] = "https://groceries.aldi.co.uk" + url

        return product_name, product_price, product_url, product_size, product_id

    def remove_spec_chars(self, input_str):
        output_str = re.sub('[,â€¦]+', ' ', input_str)
        output_str = re.sub('\s\s', ' ', output_str)
        return output_str


    def get_correct_prices(self, product_id):

        url = "https://groceries.aldi.co.uk/api/product/calculatePrices"

        querystring = {"":""}

        payload = {"products": product_id}
        headers = {
            "cookie": "AMCVS_95446750574EBBDF7F000101%40AdobeOrg=1; AMCV_95446750574EBBDF7F000101%40AdobeOrg=179643557%7CMCIDTS%7C19786%7CMCMID%7C45940883932468920850136764543741134523%7CMCAAMLH-1710090273%7C6%7CMCAAMB-1710090273%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1709492673s%7CNONE%7CMCAID%7C2F3EE68F05158457-600007946164A3D3%7CvVersion%7C5.5.0; _abck=1DB61A41B74F729E392C2AC9CAB2C63F~0~YAAQatN6XLWS3+6NAQAATEdGBQv7295UzdcU6rSuuFiI+eP6dSAOj/fWwyy34wupOod7sAIq45Ki9GtXwezhZLn3V/DA3OGndyWKvJ0alfYMM/yVf8SrR3E2gT5KPp8+7Pp3zjeksHM1wbYs3RjfNZ5GfimRaGi2HDCtRa79R72tYb0ru+cQ7W8XAmueNnmGSjnU/hnD/58T6/TH9z1dhNPy1mBMn7X3m3UbIn4mlkNXDdTTf0VXPmq29l+1YxXxNJxgyEyyJDNbFtCXJl6loMX6zgqPOZuMuwMJpYJTW8a1e46f4MQfhEnBZ8fY/I0gBJROtJEnJTXv+Nm2CCznT88uRkuuaELAj2BEYzPxU6OnjtfaX1R4JoqwIw3P9d1mO3JfoW1D4GY3TgJF8eZqq4IdhWror1fa~-1~||-1||~-1; OptanonAlertBoxClosed=2024-03-03T17:04:36.930Z; at_check=true; s_ips=1279; s_vnc365=1741021477332%26vn%3D1; _gcl_au=1.1.986117099.1709485478; s_nr365=1709485477993-New; s_sq=%5B%5BB%5D%5D; s_cc=true; s_tp=2679; s_ppv=https%253A%252F%252Fwww.aldi.co.uk%252F%2C48%2C48%2C1279%2C1%2C2; px_random=4; nlbi_2400122=OiSWH3hNK0OT1lpEaPXPwwAAAAB/Locux/IpXXU6SZAJ5IE9; visid_incap_2400122=aDBJEY4OTp2PyR099X5Q86et5GUAAAAAQUIPAAAAAADd8IXNyNJxtFOPOOSqO5gz; _hjSessionUser_1498364=eyJpZCI6IjFhZDBjNTM1LTIzZmMtNWQxYS1iN2RiLTQ3N2EzZGFmM2E1OSIsImNyZWF0ZWQiOjE3MDk0ODU0ODEyNzYsImV4aXN0aW5nIjpmYWxzZX0=; sessionStarted=1709485495; _hjDonePolls=993663; _hjSessionUser_2202991=eyJpZCI6IjI0NDg2OGRmLWM4NjgtNTFmZC1iNjUwLWIyM2VjZmIzNGM4ZiIsImNyZWF0ZWQiOjE3MDk0ODU0OTQ4OTIsImV4aXN0aW5nIjp0cnVlfQ==; incap_ses_868_2400122=f8KuYEP2XmFqiUd81sELDA3z5GUAAAAAoFQoaX01kTBWvo1AHc8umA==; incap_ses_9210_2400122=jTNMKR5CcWQw30NWUn7Qf4ab6GUAAAAABxqCwkYjYWjVrNTRG6kY0g==; mbox=PC#03b012314f284728a8ee280c4aeff617.37_0#1772987783|session#4674c05a35704b4eb54b84d4a52a08e1#1709744843; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Mar+06+2024+16%3A36%3A23+GMT%2B0000+(Greenwich+Mean+Time)&version=6.20.0&isIABGlobal=false&hosts=&consentId=8b3cc10f-7583-4847-8b7c-dab3db4a2d9d&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=%3B&AwaitingReconsent=false; QueueITAccepted-SDFrts345E-V3_production=EventId%3Dproduction%26QueueId%3D00000000-0000-0000-0000-000000000000%26RedirectType%3Ddisabled%26IssueTime%3D1709742985%26Hash%3D4ab6c1eeacbd655250ed0124aa43ca7677c947683f351fb470bf1ec6714697ee; .CUST_f3dbd28d-365f-4d3e-91c3-7b730b39b294=1|J+WeQXoon1OIa2k4r7jXUX+kbzcyepOeCDXyZ2FqZAtkmvf/ARig20oXqMLDunOvls88i+hclSeDoe6UyeeKjoG7geFhkcICGnEhq5Tpefh76rvGSWCA20whtiyOVe3ekNWUU5Ak4OFtex59+lLp6salEzK3E7X9BcATiPTyt+tk8drBMBDWpDhlKsRP2pJl0R28i/tPOdOdLLdDztxi0ihQ1Q90OsGf9qxlugvse0Ir3Ai8voqqBvDoUVCGa8GMchDAxcPcAco9FNmmrBEXAi0Zx4hidgHkOmNDm9Jx4P4iNLo8HgfJOvqXsdxoXOnMsOVWdb5ILUTZ7lhKSk1b/lJHu/zy/OxNpQVO5KhBdc+OvZahnugDe+vNIc89cIUcecflnsMriIAGNhvorEA0Sw==; _hjSession_2202991=eyJpZCI6IjI4NWQyMDE5LTJjMjQtNDg4My05MDZhLWI3YTE2MTQ0NGNkYyIsImMiOjE3MDk3NDI5ODU4NTYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=",
            "authority": "groceries.aldi.co.uk",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-GB",
            "content-type": "application/json",
            "origin": "https://groceries.aldi.co.uk",
            "referer": "https://groceries.aldi.co.uk/en-GB/fresh-food",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "websiteid": "f3dbd28d-365f-4d3e-91c3-7b730b39b294",
            "x-requested-with": "XMLHttpRequest"
        }

        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

        correct_price = re.findall(r'(?<="ListPrice":"£)[\d]+\.[\d]+', response.text)

        return correct_price