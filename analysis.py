from pymongo import MongoClient
from datetime import datetime, date, timedelta
import sys

client = MongoClient('mongodb://localhost:27017')
db = client.lianjia
c_detail = db.house_detail
c_price = db.house_price
c_meta_day = db.house_meta_day

def analyse_today(date = date.today()):
    year=date.year
    month=date.month
    day=date.day
    
    document = {
        'year':year,
        'month':month,
        'day':day
    }

    # 数据总数
    nums = c_price.find({
        'year':year,
        'month':month,
        'detail.day':day,    
    }).count()
    if nums == 0:
        return None

    # 当日均价、数量
    result = c_price.aggregate([
        { '$unwind' : "$detail" },            
        {
            '$match': {
                'year':year,
                'month':month,
                'detail.day':day,                    
            }
        },
        {
            '$group': {
                '_id': None,
                '单价': { '$avg': "$detail.单价" },
                '总数': { '$sum': 1}
            }
        },
    ])
    for item in result:
        document['当日均价'] = item['单价']
        document['当日总数'] = item['总数']

    # 面积区间

    cond = [{"$lt": ["$建筑面积", 160] }, "160-" ,"160+"]
    interval = [140,120,100,80,60] # 去除起始值
    for i in interval:
        s = str(i)
        tmp = [
            { "$lt": ["$建筑面积", i] }, s+"-", {"$cond": cond}
        ]
        cond = tmp

    result = c_price.aggregate([
        { '$unwind' : "$detail" },            
        {
            '$match': {
                'year':year,
                'month':month,
                'detail.day':day,                    
            }
        },
        {
            "$lookup":
                {
                    'from': 'house_detail',
                    'localField': 'house_id',
                    'foreignField': '_id',
                    'as': 'house_detail'
                }
        },
        {
            "$replaceRoot": { "newRoot": { "$mergeObjects": [ { "$arrayElemAt": [ "$house_detail", 0 ] }, "$$ROOT" ] } }
        },
        { "$project": { "house_detail": 0 } },
        {
            "$group": {
                "_id": {
                    "$cond": cond
                },
                "count": {"$sum": 1},
                "avg": {"$avg": "$建筑面积"},
            }
        },
        {
            "$project": {
                "count": 1,
                "percentage": {
                    "$concat": [
                        {
                            "$substr": [
                                {
                                    "$multiply": [{"$divide": ["$count", {"$literal": nums}]}, 100]
                                },
                                0,
                                5
                            ]
                        },
                        "",
                        "%"
                    ]
                }
            }
        },
    ])
    document['面积区间'] = []
    for item in result:
        document['面积区间'].append({
            '区间': item['_id'],
            '数量': item['count'],
            '百分比': item['percentage']
        })

    # 价格区间/单
    nums = c_price.find({
        'year':year,
        'month':month,
        'detail.day':day,    
    }).count()
    cond = [{"$lt": ["$detail.单价", 30000] }, "30000-" ,"30000+"]
    interval = range(28000,8000,-2000) # 去除起始值
    for i in interval:
        s = str(i)
        tmp = [
            { "$lt": ["$detail.单价", i] }, s+"-", {"$cond": cond}
        ]
        cond = tmp

    result = c_price.aggregate([
        { '$unwind' : "$detail" },            
        {
            '$match': {
                'year':year,
                'month':month,
                'detail.day':day,                    
            }
        },
        {
            "$group": {
                "_id": {
                    "$cond": cond
                },
                "count": {"$sum": 1},
                "avg": {"$avg": "$detail.单价"},
            }
        },
        {
            "$project": {
                "count": 1,
                "percentage": {
                    "$concat": [
                        {
                            "$substr": [
                                {
                                    "$multiply": [{"$divide": ["$count", {"$literal": nums}]}, 100]
                                },
                                0,
                                5
                            ]
                        },
                        "",
                        "%"
                    ]
                }
            }
        }
    ])
    document['单价区间'] = []
    for item in result:
        document['单价区间'].append({
            '区间': item['_id'],
            '数量': item['count'],
            '百分比': item['percentage']
        })

    # 价格区间/总
    cond = [{"$lt": ["$detail.总价", 400] }, "400-" ,"400+"]
    interval = range(380,40,-20) # 去除起始值
    for i in interval:
        s = str(i)
        tmp = [
            { "$lt": ["$detail.总价", i] }, s+"-", {"$cond": cond}
        ]
        cond = tmp

    result = c_price.aggregate([
        { '$unwind' : "$detail" },
        {
            '$match': {
                'year':year,
                'month':month,
                'detail.day':day,                    
            }
        },
        {
            "$group": {
                "_id": {
                    "$cond": cond
                },
                "count": {"$sum": 1},
                "avg": {"$avg": "$detail.总价"},
            }
        },
        {
            "$project": {
                "count": 1,
                "percentage": {
                    "$concat": [
                        {
                            "$substr": [
                                {
                                    "$multiply": [{"$divide": ["$count", {"$literal": nums}]}, 100]
                                },
                                0,
                                5
                            ]
                        },
                        "",
                        "%"
                    ]
                }
            }
        }
    ])
    document['总价区间'] = []
    for item in result:
        document['总价区间'].append({
            '区间': item['_id'],
            '数量': item['count'],
            '百分比': item['percentage']
        })
    # 上涨/下跌数量
    delta = timedelta(days=-1)
    newdate = date+delta
    day_asc = -1 if newdate.day < day else 1
    group_price = c_price.aggregate([
        { '$unwind' : "$detail" },
        {
            "$match": {
                '$or': [
                    {
                        'year':year,
                        'month':month,
                        'detail.day': day
                    },
                    {
                        'year':newdate.year,
                        'month':newdate.month,
                        'detail.day': newdate.day
                    },
                ]
            }
        },
        { "$sort": {'detail.day':day_asc} },
        {
            '$group': {
                '_id': {
                    "house_id": "$house_id"
                },
                'count': {'$sum': 1},
                'data': {'$push': {
                    "price":"$detail.单价",
                    "date": {
                        "year":"$year",
                        "month":"$month",
                        "day":"$detail.day",                        
                    }
                }}
            }
        },
        {
            "$match": {
                "count": 2
            }
        },
        {
            "$project": {
                'end':  { '$arrayElemAt': ["$data.price", 0] },
                'start': { '$arrayElemAt': ["$data.price", -1] },
            }
        },
        {
            "$project": {
                "isRising" : {
                    "$cond" : {
                        "if": { '$gt': [ "$start", "$end" ] },
                        "then": -1,
                        "else": {
                            "$cond": {
                                "if": {'$eq': [ "$start", "$end" ]},
                                "then": 0,
                                "else": 1
                            }
                        }
                    }
                },
                "diff": {
                    "$subtract": [ "$start", "$end" ]
                }
            }
        },
        {
            "$match": {
                '$or': [ { "isRising": 1 }, { "isRising": -1 } ]
            }
        },
        # {
        #     "$group": {
        #         "_id": {
        #             "rising":"$isRising",
        #         },
        #         "count": {"$sum":1}
        #     }
        # }
        {
            "$sort": { "diff" : 1 }
        }
    ])
    document['涨跌数量'] = {
        "上涨": 0,
        "下跌": 0
    }

    document['跌幅最大'] = None
    start = True
    document['涨幅最大'] = None
    for item in group_price:
        if start:
            document['跌幅最大'] = item
            start = False
        if item['isRising'] == 1:
            document['涨跌数量']['上涨'] += 1
        elif item['isRising'] == -1:
            document['涨跌数量']['下跌'] += 1
    if item != None:
        document['涨幅最大'] = item #last one


    # todo:今日最贵小区

    # 写入数据库
    c_meta_day.replace_one(
    {
        'year':year,
        'month':month,
        'day':day
    },
    document,
    upsert=True)
    return document


    def most_house_in_community(self):
        '''
        # 房屋数量最多的小区
        '''
        result = self.collection.aggregate([
            {
                '$group': {
                    '_id': "$小区名称",
                    'count': {'$sum': 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ])
        for i in result:
            print(i)

    def group_by_aera(self):  # 按区间聚合房屋面积
        nums = self.collection.find().count()
        result = self.collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$lt": ["$建筑面积", 100]},
                            "0-100",
                            {
                                "$cond": [
                                    {"$lt": ["$建筑面积", 150]},
                                    "100-150",
                                    "150+"
                                ]
                            }
                        ]
                    },
                    "count": {"$sum": 1},
                    "avg": {"$avg": "$建筑面积"},
                }
            },
            {
                "$project": {
                    "count": 1,
                    "percentage": {
                        "$concat": [
                            {
                                "$substr": [
                                    {
                                        "$multiply": [{"$divide": ["$count", {"$literal": nums}]}, 100]
                                    },
                                    0,
                                    2
                                ]
                            },
                            "",
                            "%"
                        ]
                    }
                }
            }
        ])
        print('房屋面积比例')
        for i in result:
            print(i)

if __name__ == '__main__':
    count = len(sys.argv)
    if len(sys.argv) == 1:
        begin = datetime.today()
        end = datetime.today()
    elif len(sys.argv) == 2:
        begin = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        end = datetime.today()
    else:
        begin = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        end = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    print('begin:',begin,'end:',end)


    for i in range((end - begin).days + 1):
        day = begin + timedelta(days=i)
        doc = analyse_today(day)
        if doc != None:
            print(doc['year'],doc['month'],doc['day'])



    # analyse_today(datetime.strptime('2018-12-20', '%Y-%m-%d'))
