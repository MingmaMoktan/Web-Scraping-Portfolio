import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    
    # This line of code is to extract the simple title, price and url to the book which also includes the pagination to go throught the different pages of the website.

    '''def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css("p.price_color::text").get(),
                "link": book.css("h3 a::attr(href)").get(),
            }
        # This is for the pagination which means going through the different pages.
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse) # Here callback is the function that will be called to handle the response downloaded for this request. The response parameter is an instance of TextResponse that holds the page content and has further helpful methods to handle it.
    '''
        # This line of code is to extract the details of each book going through the url of each book and extracting the details from the book page. 
    def parse(self, response):
    # 1. Extract books and follow their detail pages
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book_details)
            
        # 2. Handle Pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
            
    def parse_book_details(self, response):
    # Selectors for the individual product detail page
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "stock": response.css("p.instock.availability::text").getall(),
            "link": response.url,
        }