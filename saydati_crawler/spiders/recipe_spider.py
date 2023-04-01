from pathlib import Path
import scrapy

class RecipesSpider(scrapy.Spider):
    name = "recipes"
    start_urls = [
        "https://kitchen.sayidaty.net/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D9%88%D8%B5%D9%81%D8%A7%D8%AA"
    ]
    

    def parse(self, response):
        cuisine_links = response.xpath('//select[@name="cuisine"]').css ('option:nth-child(n+3)::attr(value)')
        yield from response.follow_all(cuisine_links, self.parse_cuisine)
        
    def parse_cuisine(self, response):
        recipe_page_links = response.css('div.article-item-img a::attr(href)')
        cuisine = response.css('div.topper-title h1::text').get()
        passme = dict(key = cuisine)
        yield from response.follow_all(recipe_page_links, callback=self.parse_recipe, cb_kwargs=passme)
    
        pagination_links = response.css('ul.pagination li a')
        yield from response.follow_all(pagination_links, self.parse_cuisine)
        
    def parse_recipe(self, response, key):
        recipe_name = response.css('div.topper-title h1::text').get()
        recipe_description = response.css('div.intro-text p span::text').get()
        recipe_time = response.css('div.recipe-meta-data-info span::text').get()
        recipe_ingredients = response.css('div.ingredients-area::text').getall()
        recipe_steps = response.css('div.preparation-area ol li span::text').getall()
        recipe_tags = response.css('div.tags-area a::text').getall()
        #recipe ingredients and steps are not extracted correctly 
        #remove /n and /t from the lis
        recipe_ingredients = [i.strip() for i in recipe_ingredients if i.strip()]
        recipe = {
            'name': recipe_name,
            'ingredients': recipe_ingredients,
            'steps': recipe_steps,
            'description': recipe_description,
            'time': recipe_time,
            'tags': recipe_tags,
            'cuisine': key
        }
        yield recipe