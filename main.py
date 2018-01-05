import urllib.request
import os
import re
import codecs
from HouseDetail import get_house_detail
import HouseDetail
from pymongo import MongoClient




conn = MongoClient('localhost', 27017)
db = conn.lianjia  #连接mydb数据库，没有则自动创建
myset = db.house_detail#使用test_set集合，没有则自动创建

f = codecs.open("house_list.txt", "r", "UTF-8")
house_list = eval(f.read())
house_list_delete = {}
for (key,value) in house_list.items():
    id =  int(re.findall(r"[0-9]+", key)[0])
    print("开始读取url:",key,end="...")
    if not myset.find_one({"_id":id}):
        try:
            html = urllib.request.urlopen(key)
            house = get_house_detail(html)
            print("成功!",end="")
            myset.insert(house)
            print("写入数据库成功!")
        except urllib.error.HTTPError as e:
            house_list_delete[key] = value
            print(e.code, e.reason)
        except Exception as e:
            print(e)
    else:
        print("发现重复键，未写入数据库!")

    # myset.update( document = house, upsert=True)


print("asdf;asdkfj")