# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item
from scrapy import Field


class ErShouFangItems(Item):
    house_code = Field()  # 二手房ID
    # house_area = Field() # 面积
    # list_pic_url = Field() # 图片url
    # title = Field() # 标题
    # frame_type = Field() # 户型
    # floor_level = Field() # 楼层
    # floor_total = Field() # 总楼层
    # orientation = Field() 
    # building_type = Field() 
    # decoration_type = Field() 
    # building_year = Field() 
    # deal_property = Field() #交易属性
    # list_time = Field() # 挂牌时间
    # house_type = Field() #住房用途
    # elevator = Field()
    # total_price = Field()
    # elevator = Field()
    # list_price = Field()
    # unit_price = Field()
    # elevator = Field()
    # elevator = Field()
    

    resblock_id = Field()  # 小区ID
    resblock_name = Field()  # 小区名字
    price = Field()  # 价格元/平
