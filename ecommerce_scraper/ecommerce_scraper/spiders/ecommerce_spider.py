import scrapy


class EcommerceSpiderSpider(scrapy.Spider):
    name = "ecommerce_spider"
    allowed_domains = ["www.scrapingcourse.com"]
    start_urls = ["https://www.scrapingcourse.com/ecommerce/"]

    def parse(self, response):
        products = response.css("li.product")
        for product in products:
            yield {
                "title" : product.css("h2.woocommerce-loop-product__title::text").get(),
                "price" : product.css("span.woocommerce-Price-amount bdi::text").get(),
                "image_url" : product.css("img::attr(src)").get(),
                "link" : product.css("a.woocommerce-LoopProduct-link::attr(href)").get(),
            }
        next_page = response.css("a.next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
    