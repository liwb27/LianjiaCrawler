import scrapy
from scrapy.utils.project import get_project_settings
import time
import json
import math
from LianjiaCrawler.items import ErShouFangItems
from LianjiaCrawler.ljapi.weixin import get_request


class LianjiaSpiderWx(scrapy.Spider):
    name = 'ljapi'
    limit = 30
    def start_requests(self):
        """
        重写start_requests
        :return:
        """
        yield get_request(self.settings["CITY_ID"], 0, self.limit, self.parse)
        # yield get_community_info(self.settings["CITY_ID"], self.parse)

    def parse(self, response):
        content = json.loads(response.body.decode())
        total_count = int(content["data"]["total_count"])
        total_count = int(math.ceil(total_count / self.limit)) # 获取一共有多少页面数据

        self.parse_house_item(response)
        limit_offset = 0
        for _ in range(0, total_count):  # 翻页操作
            limit_offset += self.limit  # 每页显示self.limit条数据，每次翻页递增self.limit条
            yield get_request(self.settings["CITY_ID"], limit_offset, self.parse_house_item)

    def parse_house_item(self, response):
        """
        解析JSON 数据
        :param response:
        :return:
        """
        item = ErShouFangItems()
        content = json.loads(response.body.decode())
        ershoufang_list = content["data"]["list"]
        if len(ershoufang_list) > 0:
            for ershoufang in ershoufang_list:
                # for key,val in item.fields.items():
                #     item[key] = ershoufang_list[ershoufang][key]
                item["house_code"] = ershoufang_list[ershoufang]["house_code"]
                item["resblock_id"] = ershoufang_list[ershoufang]["resblock_id"]
                item["resblock_name"] = ershoufang_list[ershoufang]["resblock_name"]
                yield item

