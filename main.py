import urllib.request
import os
import re
import codecs
from pymongo import MongoClient
from HouseDetail import get_houselist_detail
from HouseList import get_house_list

#控制参数
is_offline = False #是否重新爬取房源列表
is_update_db = True #是否更新数据库中已有条目
mongo_conn = MongoClient('localhost', 27017) #数据库连接
url = "https://zz.lianjia.com/ershoufang/" #链家二手房链接，可爬取不同城市

#获取房源列表
house_list = get_house_list(url, offline = is_offline)

(house_list_delete, house_list_error) = get_houselist_detail(house_list, mongo_conn, update = is_update_db)

#记录完成情况
finish = len(house_list)
delete = len(house_list_delete)
err = len(house_list_error)
print("任务结束，成功" + str(finish - delete - err) + "条，消失" + str(delete) + "条，出错" + str(err) + "条。")
print("详见house_list_delete.txt, house_list_error.txt")
#存储已消失房源列表
f = codecs.open("house_list_delete.txt", "r", "UTF-8")
house_list_delete_fromfile = eval(f.read())
f.close()
f = codecs.open("house_list_delete.txt", "w", "UTF-8")
f.write(str(list(set(house_list_delete) | set(house_list_delete_fromfile))))
f.close()
#存储错误列表
f = codecs.open("house_list_error.txt", "w", "UTF-8")
f.write(str(house_list_error))
f.close()
#存储房源列表
# house_list_success = set(house_list) - set(house_list_delete)
# f = codecs.open("house_list.txt", "w", "UTF-8")
# f.write(str(house_list_success))
# f.close()