import scrapy

class IEEEReferencesSpider(scrapy.Spider):
	name = "IEEEReferences"
	urls = []

	def setUrls(init_urls):
		urls = init_urls

	def start_requests(self):
		start_urls = ['http://quotes.toscrape.com/page/1/','http://quotes.toscrape.com/page/2/',]
		for url in start_urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		page = response.url.split("/")[-2] # split url at the second / from the right
		filename = 'quotes-%s.html' % page # filename for html file
		with open(filename, 'wb') as f:	   # writing 
			f.write(response.body)
		self.log('Saved file %s' % filename)