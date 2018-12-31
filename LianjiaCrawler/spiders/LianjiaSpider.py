import scrapy
from scrapy.shell import inspect_response
from LianjiaCrawler.items import ErShouFangItems

class LianjiaSpider(scrapy.Spider):
    name = "lianjia"
    
    def start_requests(self):
        urls = [
            'https://zz.lianjia.com/ershoufang/',
            # 'https://zz.lianjia.com/ershoufang/2',            
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        '''
        从首页开始，爬取区域列表
        '''
        for aera in response.xpath('//div[@data-role="ershoufang"]/div/a'):
            name = aera.xpath('text()').extract_first()
            url = aera.xpath('@href').extract_first()
            url = response.urljoin(url)
            if url is not None:
                self.log('区域：{0}, URL: {1}'.format(name, url))
                yield scrapy.Request(url=url, callback=self.parse_aera)

        # inspect_response(response, self)

    def parse_aera(self, response):
        '''
        爬取子区域
        '''
        page_total = int(response.css('.page-box.house-lst-page-box').xpath('@page-data').re(r"(?<=\"totalPage\":)\d*")[0])
        # if page_total < 100:
        #     self.parse_page(response)
        #     for i in range(2, page_total+1):
        #         yield scrapy.Request(url=response.url + 'pg' + str(i), callback=self.parse_page)
        # else:
        for item in response.xpath('//div[@data-role="ershoufang"]/div[2]/a'):
            name = item.xpath('text()').extract_first()
            url = item.xpath('@href').extract_first()
            self.log('子区域：{0}, 共{1}页, URL: {2}'.format(name, page_total, url))
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_subaera)
    
    def parse_subaera(self, response):
        # self.log('parse_subaera: {0}'.format(response.url))
        page_data = response.css('.page-box.house-lst-page-box').xpath('@page-data').re(r"(?<=\"totalPage\":)\d*")
        if len(page_data) != 0:
            page_total = int(page_data[0])
            if page_total > 100:
                self.log('子区域房源过多，存在部分房源丢失！: {0}'.format(response.url))
            self.parse_page(response)
            for i in range(2, page_total+1):
                yield scrapy.Request(url=response.url + 'pg' + str(i), callback=self.parse_page)
        else:
            page_total = 0


    def parse_page(self, response):
        # self.log('parse_page: {0}'.format(response.url))
        # todo parse house 
        return ErShouFangItems()
    
    def parse_detail(self, response):
        # self.log('parse_detail: {0}'.format(response.url))
        pass