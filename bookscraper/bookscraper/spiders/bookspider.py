import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
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
            