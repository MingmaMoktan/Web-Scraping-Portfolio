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
            value = adapter.get(key)
            if isinstance(value, str):
                adapter[key] = value.lower()
            
        ## Price fields --> remove pound symbol and convert to float
        price_keys = ['price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if isinstance(value, str):
                value = value.replace('£', '').strip()
                adapter[price_key] = float(value)
    
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
        if num_reviews_string is not None:
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

        return item
    
from sqlalchemy import create_engine, text

class SaveToPostgresPipeline:
    def open_spider(self, spider):
        # 1. Open the connection when spider starts
        # Format: postgresql://username:password@localhost:5432/dbname
        db_url = 'postgresql://postgres:Dm%401995@localhost:5432/book'
        self.engine = create_engine(db_url)
        self.conn = self.engine.connect()

    def process_item(self, item, spider):
        # 2. Extract values directly from item
        url_val = item.get('url')[0] if isinstance(item.get('url'), list) else item.get('url')

        # 3. Insert into PostgreSQL using raw SQL
        query = text("""
            INSERT INTO books (url, title, upc, product_type, price_excl_tax, price_incl_tax, 
                               tax, availability, num_reviews, stars, category, description, price)
            VALUES (:url, :title, :upc, :product_type, :price_excl_tax, :price_incl_tax, 
                    :tax, :availability, :num_reviews, :stars, :category, :description, :price)
        """)

        self.conn.execute(query, {
            'url': url_val,
            'title': item.get('title'),
            'upc': item.get('upc'),
            'product_type': item.get('product_type'),
            'price_excl_tax': item.get('price_excl_tax'),
            'price_incl_tax': item.get('price_incl_tax'),
            'tax': item.get('tax'),
            'availability': item.get('availability'),
            'num_reviews': item.get('num_reviews'),
            'stars': item.get('stars'),
            'category': item.get('category'),
            'description': item.get('description'),
            'price': item.get('price')
        })
        self.conn.commit()
        return item

    def close_spider(self, spider):
        # 4. Close connection when done
        self.conn.close()