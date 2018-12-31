# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class LianjiacrawlerPipeline(object):
    count = 0
    def process_item(self, item, spider):
        self.count += 1
        print('-------current count:{0} ---------'.format(self.count))
        return item
