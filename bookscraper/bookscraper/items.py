# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# This function below is used to serialize the price field in the BookItem class. It takes a value as input and returns a string formatted with the pound symbol (£) followed by the value. This function can be used to ensure that the price is consistently formatted when storing or displaying it.
def serialize_price(value):
    return f'£ {str(value)}'

class BookItem(scrapy.Item):
   url = scrapy.Field()
   title = scrapy.Field()
   upc = scrapy.Field()
   product_type = scrapy.Field()
   price_excl_tax = scrapy.Field(serializer=serialize_price)  # Use the serialize_price function to format the price_excl_tax field
   price_incl_tax = scrapy.Field(serializer=serialize_price)  # Use the serialize_price function to format the price_incl_tax field
   tax = scrapy.Field()
   availability = scrapy.Field()
   num_reviews = scrapy.Field()
   stars = scrapy.Field()
   category = scrapy.Field()
   description = scrapy.Field()
   price = scrapy.Field()