# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from pymongo import MongoClient
import re
from datetime import datetime, date
from LianjiaCrawler.items import HouseItem, PriceItem


class LianjiacrawlerPipeline(object):
    def __init__(self, mongo_uri, mongo_db, mongo_collection, price_collection):
        self.count = 0
        self.seen_house = set()
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.price_collection = price_collection

    @classmethod
    def from_crawler(cls, crawler):
        '''
            scrapy为我们访问settings提供了这样的一个方法，这里，
            我们需要从settings.py文件中，取得数据库的URI和数据库名称
        '''
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DBNAME'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION_NAME'),
            price_collection=crawler.settings.get('MONGO_COLLECTION_PRICE_NAME'),
        )

    def open_spider(self, spider):
        '''
        爬虫一旦开启，就会实现这个方法，连接到数据库
        '''
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]
        self.collection2 = self.db[self.price_collection]

    def close_spider(self, spider):
        '''
        爬虫一旦关闭，就会实现这个方法，关闭数据库连接
        '''
        self.client.close()
    
    def process_item(self, item, spider):
        if type(item) == HouseItem:
            house = item['data']
            self.collection.replace_one({'_id': house['_id']}, house, upsert=True)
            # self.count += 1
            # logging.info('---update house----current count:{0} ---------'.format(self.count))
        elif type(item) == PriceItem:
            price = item['data']
            exist = self.collection2.find_one({
                "house_id": price['house_id'],
                'year': price['date'].year,
                'month': price['date'].month,
                'detail.day': {'$eq': price['date'].day}
            })
            if not exist:
                self.collection2.update_one(
                    {
                        'house_id': price['house_id'],
                        'year': price['date'].year,
                        'month': price['date'].month,
                    },
                    {
                        '$push': { 'detail': {'day': price['date'].day,'单价':price['单价'],'总价':price['总价']}},
                        '$inc': { 'detailCount': 1}
                    },
                    upsert=True)
            else:
                self.collection2.update_one(
                    {
                        'house_id': price['house_id'],
                        'year': price['date'].year,
                        'month': price['date'].month,
                        'detail.day':price['date'].day,
                    },
                    {
                        '$set':{
                            'detail.$.单价':price['单价'],
                            'detail.$.总价':price['总价'],                            
                        }
                    }
                )
                
            self.count += 1
            if self.count % 100 == 0:
                logging.info('---update price----current count:{0} ---------'.format(self.count))
        return item

