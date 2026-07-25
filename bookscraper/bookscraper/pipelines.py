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
        # 1. Connect using SQLAlchemy engine
        db_url = 'postgresql://postgres:Dm%401995@localhost:5432/book'
        self.engine = create_engine(db_url)
        self.conn = self.engine.connect()
    
        # 2. Create table using explicit commit
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                url TEXT,
                title VARCHAR(255),
                upc VARCHAR(255),
                product_type VARCHAR(255),
                price_excl_tax NUMERIC(10, 2),
                price_incl_tax NUMERIC(10, 2),
                tax NUMERIC(10, 2),
                availability INT,
                num_reviews INT,
                stars INT,
                category VARCHAR(255),
                description TEXT,
                price VARCHAR(50)
            );
        """)
        
        # Use explicit transaction block for table creation
        with self.conn.begin():
            self.conn.execute(create_table_query)

    def process_item(self, item, spider):
        # Unpack URL if it's wrapped in a list/tuple
        url_raw = item.get("url")
        if isinstance(url_raw, (list, tuple)) and len(url_raw) > 0:
            url_val = str(url_raw[0])
        else:
            url_val = str(url_raw) if url_raw else None

        query = text("""
            INSERT INTO books (
                url, title, upc, product_type, price_excl_tax, price_incl_tax, 
                tax, availability, num_reviews, stars, category, description, price
            )
            VALUES (
                :url, :title, :upc, :product_type, :price_excl_tax, :price_incl_tax, 
                :tax, :availability, :num_reviews, :stars, :category, :description, :price
            )
        """)

        # Using "with self.conn.begin():" automatically commits if successful,
        # and automatically rolls back if an error occurs.
        try:
            with self.conn.begin():
                self.conn.execute(
                    query,
                    {
                        "url": url_val,
                        "title": item.get("title"),
                        "upc": item.get("upc"),
                        "product_type": item.get("product_type"),
                        "price_excl_tax": item.get("price_excl_tax"),
                        "price_incl_tax": item.get("price_incl_tax"),
                        "tax": item.get("tax"),
                        "availability": item.get("availability"),
                        "num_reviews": item.get("num_reviews"),
                        "stars": item.get("stars"),
                        "category": item.get("category"),
                        "description": item.get("description"),
                        "price": str(item.get("price")),
                    },
                )
            spider.logger.info(f"Successfully saved to DB: {item.get('title')}")
        except Exception as e:
            spider.logger.error(f"Database Insert Error for '{item.get('title')}': {e}")

        return item

    def close_spider(self, spider):
        # Close the connection cleanly when finished
        self.conn.close()
        self.engine.dispose()