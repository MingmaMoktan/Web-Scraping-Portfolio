# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        ## Strip all whitespace from string fields
        field_names =  adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                if isinstance(value, str):
                    adapter[field_name] = value.strip()
        
        ## Category and product type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for key in lowercase_keys:
            value = adapter.get(lowercase_keys)
            adapter[lowercase_keys] = value.lower()
            
            
        ## Price fields --> remove pound symbol and convert to float
        price_keys = ['price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if isinstance(value, str):
                value = value.replace('£', '').strip()
                adapter[price_key] = float(value)
        return item
    
        ## Availability field --> extract number of available items
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_number_string = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_number_string[0])
            
        ## Review field --> convert to integer
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)
        
        ## Stars field --> convert to integer
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower()
        stars_dict = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5
        }
        adapter['stars'] = stars_dict.get(stars_text_value, 0)
