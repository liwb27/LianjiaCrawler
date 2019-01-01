# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from pymongo import MongoClient
import re
from datetime import datetime, date
from LianjiaCrawler.items import ErShouFangItems

MONGO_CONN = MongoClient('localhost', 27017)  # 连接
db = MONGO_CONN.lianjia
myset = db.house_detail

class LianjiacrawlerPipeline(object):
    count = 0
    # seen_house = set()
    def process_item(self, item, spider):
        if type(item) == ErShouFangItems:
            # if item['house_code'] in self.seen_house:
            #     raise Exception("Duplicate house found:%s" % item['house_code'])
            house = {}
            house['_id'] = int(item['house_code'])
            house['title'] = item['title']
            house['小区名称'] = item['resblock_name']
            house['小区id'] = item['resblock_id']
            house['房屋户型'] = parse_huxing(item['frame_type'])
            house['建筑面积'] = float(item['house_area'])
            house['房屋朝向'] = item['orientation']
            house['装修情况'] = item['decoration_type']
            # house['所在区域'] = ?
            house['所在楼层'] = item['floor_level']
            house['总楼层'] = item['floor_total']
            house['楼型'] = item['building_type']
            # 关注人数 = ？
            # 带看人数 = ？
            house['tag'] = [tag['title'] for tag in item['tags']]
            try:
                house['挂牌时间'] = datetime.strptime(item['list_time'],'%Y.%m.%d')
            except:
                house['挂牌时间'] = item['list_time']
            house['建筑年代'] = item['building_year'] # 是否都是'--'
            house['交易属性'] = item['deal_property']
            house['住房用途'] = item['house_type']
            house['电梯'] = item['elevator']
            house['is_sold'] = item['is_sold']
            house['is_focus'] = item['is_focus']
            house['is_remove'] = item['is_remove']
            house['is_yezhu_rec'] = item['is_yezhu_rec']
            house['地铁'] = item['subway_info']
            # 按照爬虫时间记录
            price = {
                'date': datetime.strptime(str(date.today()),'%Y-%m-%d'),
                '总价': item['total_price'],
                '挂牌价': item['list_price'],
                '单价': item['unit_price'],
            }
            # 查找数据库中是否存在该记录
            old_house = myset.find_one({"_id": house['_id']})
            if not old_house: # 新记录
                house['价格'] = []
                house['价格'].append(price)
                myset.insert(house)
            else: # 旧记录
                old_house.update(house)
                isTodayFlag = False
                for p in old_house["价格"]:
                    if p['date'] == datetime.strptime(str(date.today()),'%Y-%m-%d'):
                        isTodayFlag = True
                        break
                if not isTodayFlag:
                    old_house["价格"].append(price)
                myset.save(old_house)
            self.count += 1
            # self.seen_house.add(item['house_code'])
            logging.info('-------current count:{0} ---------'.format(self.count))
        return item


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