from pymongo import MongoClient
from datetime import datetime, date

def fun1():
    # 重构数据存储结构
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

def fun2():
    # 将按天存储改为按月存储
    client = MongoClient('mongodb://localhost:27017')
    db = client.lianjia
    c_old = db.house_price
    c_new = db.house_price_per_month
    i = -1
    dup = 0
    for item in c_old.find({},no_cursor_timeout = True,batch_size=1000):
        date = item['date']
        # exist = c_new.find_one({
        #     "house_id": item['house_id'],
        #     'year': date.year,
        #     'month': date.month,
        #     'detail.day': {
        #         '$eq': date.day
        #     }
        #     })
        # if not exist:
        c_new.update_one(
            {
                'house_id': item['house_id'],
                'year': date.year,
                'month': date.month,
                # 'ncount': 0,
            },
            {
                '$push': { 'detail': {'day': date.day,'单价':item['单价'],'总价':item['总价']}},
                '$inc': { 'detailCount': 1}
            },
            upsert=True)
        i = i+1
        # else:
        #     dup = dup + 1
        #     # print('duplicate day')
        if i % 1000 == 0:
            print(str(i) + ',  dup:' + str(dup))

    c_old.rename('old_price')
    c_new.rename('house_price')

if __name__ == '__main__':
    fun2()