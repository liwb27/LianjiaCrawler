import scrapy
from scrapy.utils.project import get_project_settings
import logging
import json
import re
import datetime
from pymongo import MongoClient
from LianjiaCrawler.items import HouseItem, PriceItem
from LianjiaCrawler.ljapi.mobileapp import get_city_info


class LianjiaSpider(scrapy.Spider):
    name = "lianjia"
    def __init__(self, update_mode=False, *args, **kwargs):
        super(LianjiaSpider, self).__init__(*args, **kwargs)
        # update_mode = true时，强制重新爬取每个房源的页面
        # 否则，会检查数据库中是否存在该房源，如存在则只增量更新当日价格，如不存在则爬取该房源信息
        self.update_mode = update_mode
        self.settings = get_project_settings()
        self.collection = MongoClient(self.settings['MONGO_URI'])[self.settings['MONGO_DBNAME']][self.settings['MONGO_COLLECTION_NAME']]
        self.price_collection = MongoClient(self.settings['MONGO_URI'])[self.settings['MONGO_DBNAME']][self.settings['MONGO_COLLECTION_PRICE_NAME']]

    def start_requests(self):
        yield get_city_info(self.settings['CITY_ID'], self.parse)

    def parse(self, response):
        '''
        分析get_city_info结果，并准备按照bizcircle进行爬取
        '''
        try:
            city_info = json.loads(response.body.decode())['data']['city_info']['info'][0]
        except:
            self.log('读取城市信息失败', level=logging.ERROR)
            return
        if city_info['city_id'] != int(self.settings['CITY_ID']):
            self.log('错误的城市ID:'+ city_info['city_id'], level=logging.ERROR)
            return
        self.subway = city_info['subway_line'] # 记录地铁信息
        for district in city_info['district']:
            for bizcircle in district['bizcircle']:
                url = self.settings['BASE_URL'] + '/ershoufang/' + bizcircle['bizcircle_quanpin'] + '/'
                yield scrapy.Request(url=url, callback=self.parse_bizcircle, meta={'bizcircle':bizcircle})
    
    def parse_bizcircle(self, response):
        page_data = response.css('.page-box.house-lst-page-box').xpath('@page-data').re(r"(?<=\"totalPage\":)\d*")
        bizcircle = response.meta['bizcircle']
        if len(page_data) != 0:
            page_total = int(page_data[0])
            if page_total > 100:
                self.log('子区域房源过多，存在部分房源丢失！: {0}'.format(response.url), level=logging.WARNING)
            self.parse_page(response)
            for i in range(2, page_total+1):
                yield scrapy.Request(url=response.url + 'pg' + str(i) + '/', callback=self.parse_page, meta={'bizcircle': bizcircle} )
        else:
            page_total = 0


    def parse_page(self, response):
        bizcircle = response.meta['bizcircle']        
        for item in response.css('.clear.LOGCLICKDATA'):
            id = int(item.xpath('./a/@href').re(r"[0-9]+")[0])
            old_house = self.collection.find_one({"_id": id})
            if not old_house or self.update_mode: # 未收集过详细信息，或强制收集详细信息
                url = self.settings['BASE_URL'] + '/ershoufang/{0}.html'.format(id)
                yield scrapy.Request(url=url, callback=self.parse_detail, meta={'new':id, 'bizcircle': bizcircle})
            # 解析价格，并发给pipeline
            date = datetime.datetime.strptime(str(datetime.date.today()),'%Y-%m-%d')
            today = self.price_collection.find_one({"house_id": id, 'date': date})
            if not today:
                price = {}
                priceItem = PriceItem()
                priceItem['data'] = price
                price['house_id'] = id
                price['date'] = date
                price['总价'] = float(item.css('.totalPrice').xpath('./span').re('[0-9.]+')[0])
                price['单价'] = float(item.css('.unitPrice').xpath('./span').re('[0-9.]+')[0])
                # todo 关注、带看。。。
                # self.log('parse house price: {0}'.format(id), level=logging.INFO)
                yield priceItem
    
    def parse_detail(self, response):
        house = {}
        house_item = HouseItem()
        house_item['data'] = house
        house['_id'] = int(response.css('.houseRecord').css('.info').xpath('./text()').extract_first()) 
        house['标题'] = ''# title
        house['关注数'] = int(response.xpath('//*[@id="favCount"]/text()').extract_first()) # 关注
        house['小区名称'] = response.css('.communityName').css('.info').xpath('./text()').extract_first()
        house['小区id'] = int(response.css('.communityName').css('.info').xpath('./@href').re(r"[0-9]+")[0])
        house['商圈名称'] = response.meta['bizcircle']['bizcircle_name']
        house['商圈id'] = response.meta['bizcircle']['bizcircle_id']
        subwar_href = response.css('.areaName').xpath('./a/@href').extract_first()
        if subwar_href != '':
            line_id = re.findall(r"li[0-9]+", subwar_href)[0][2:]
            station_id = re.findall(r"s[0-9]+", subwar_href)[0][1:]
            for line in self.subway:
                if line['subway_line_id'] == line_id:
                    for station in line['station']:
                        if station['subway_station_id'] == station_id:
                            house['地铁'] = {
                                '线路': line['subway_line_name'],
                                '车站': station['subway_station_name'],
                            }
                            break
        # 基本信息
        for selector in response.css('.introContent').css('.base').css('.content').xpath('./ul/li'):
            label = selector.xpath('./span/text()').extract_first()
            text = selector.xpath('./text()').extract_first()
            house[label] = house_detail_switcher(label)(text.strip('\n'))
        # 交易属性
        for selector in response.css('.introContent').css('.transaction').css('.content').xpath('./ul/li'):
            label = selector.xpath('./span/text()').extract_first()
            text = selector.xpath('./span[2]/text()').extract_first()
            house[label] = house_detail_switcher(label)(text.strip('\n').strip())
        # tag
        house['tag'] = response.css('.tags.clear').css('.content').xpath('./a/text()').extract()
        # 房源特色 无用

        # self.log('parse house detail: {0}'.format(house['_id']), level=logging.INFO)
        yield house_item

def house_detail_switcher(label):
    def parse_huxing(text):
        ting = re.findall(r"\d(?=室)", text)
        if ting != []:
            ting = int(ting[0])
        else:
            ting = 0
        shi = re.findall(r"\d(?=厅)", text)
        if shi != []:
            shi = int(shi[0])
        else:
            shi = 0
        chu = re.findall(r"\d(?=厨)", text)
        if chu != []:
            chu = int(chu[0])
        else:
            chu = 0
        wei = re.findall(r"\d(?=卫)", text)
        if wei != []:
            wei = int(wei[0])
        else:
            wei = 0
        return {
            "室": ting,
            "厅": shi,
            "厨": chu,
            "卫": wei,
        }

    # def parse_tihu(text):
    #     chs_arabic_map = {u"零": 0, u"一": 1, u"二": 2, u"三": 3, u"四": 4, u"五": 5, u"六": 6, u"七": 7, u"八": 8, u"九": 9, u"两": 2,
    #                       u"十": 10, u"十一": 11, u"十二": 12, u"十三": 13, u"十四": 14, u"十五": 15, u"十六": 16, u"十七": 17, u"十八": 18, u"十九": 19}
    #     ti = re.findall(r".(?=梯)", text)
    #     if ti != []:
    #         ti = chs_arabic_map[ti[0]]
    #     else:
    #         ti = 0
    #     hu = re.findall(r".(?=户)", text)
    #     if hu != []:
    #         hu = chs_arabic_map[hu[0]]
    #     else:
    #         hu = 0

    #     return {
    #         "梯": ti,
    #         "户": hu,
    #     }

    def parse_size(text):
        size = re.findall(r"[0-9.]+(?=㎡)", text)
        if size != []:
            return float(size[0])
        else:
            return None

    def parse_year(text):
        year = re.findall(r"\d+(?=年)", text)
        if year != []:
            return int(year[0])
        else:
            return None

    def parse_date(text):
        try:
            return datetime.datetime.strptime(text, "%Y-%m-%d")
        except:
            return text

    # def parse_louceng(text):
    #     floor_text = text.split('(')
    #     if len(floor_text) > 1:
    #         return {
    #             '所在楼层': floor_text[0],
    #             '总楼层': floor_text[1].split(')')[0]
    #         }
    #     else:
    #         return {
    #             '所在楼层': floor_text
    #         }


    # 属性解析器
    switcher = {
        "房屋户型": parse_huxing,
        "建筑面积": parse_size,
        "套内面积": parse_size,
        # "房屋朝向": lambda text: text.split(),
        # "梯户比例": parse_tihu,
        "产权年限": parse_year,
        "挂牌时间": parse_date,
        "上次交易": parse_date,
        # "所在楼层": parse_louceng,
    }

    return switcher.get(label, lambda text: text) # 没有特殊解析器的就直接返回文字
