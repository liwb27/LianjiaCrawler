import urllib.request
import os
import re
import codecs
from pymongo import MongoClient
from HouseDetail import get_houselist_detail
from HouseList import get_house_list

#写入User Agent信息
url = "https://zz.lianjia.com/ershoufang/"
head = {}
head['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
req = urllib.request.Request(url, headers=head)

#获取房源列表
house_list = get_house_list(url, offline = False)

(house_list_delete, house_list_error) = get_houselist_detail(house_list, MongoClient('localhost', 27017))

#记录完成情况
finish = len(house_list)
delete = len(house_list_delete)
err = len(house_list_error)
print("任务结束，成功" + str(finish - delete - err) + "条，消失" + str(delete) + "条，出错" + str(err) + "条。")
print("详见house_list_delete.txt, house_list_error.txt")
f = codecs.open("house_list_delete.txt", "w", "UTF-8")
f.write(str(house_list_delete))
f.close()

f = codecs.open("house_list_error.txt", "w", "UTF-8")
f.write(str(house_list_error))
f.close()
