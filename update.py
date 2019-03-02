from pymongo import MongoClient
from datetime import datetime, date

# 重构数据存储结构

if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017')
    db = client.lianjia
    collection = db.house_detail
    c2 = db.house_price
    i = 0
    for item in collection.find():
        price = item.pop('价格', [])
        for day in price:
            new_item = {
                'house_id': item['_id'],
                'date': day['date'],
                '总价': day['总价'],
                '单价': day['单价'],
            }
            c2.insert(new_item)
        collection.replace_one({'_id': item['_id']}, item, upsert=True)
        i += 1
        print(i)