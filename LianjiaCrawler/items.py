# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item
from scrapy import Field

class PriceItem(Item):
    data = Field()
    id = Field()
    # totalPrice = Field()
    # unitPrice = Field()

class HouseItem(Item):
    data = Field()




