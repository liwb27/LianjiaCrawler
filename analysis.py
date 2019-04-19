from pymongo import MongoClient
from datetime import datetime, date
# todo: '价格'array随时间增长，过大时需要将其拆分成单独collection


class Analysis(object):
    client = MongoClient('mongodb://localhost:27017')
    db = client.lianjia
    collection = db.house_detail
    collection_price = db.house_price
    

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
 
    # 小区均价
    def group_by_community(self, date=datetime.strptime(str(date.today()), '%Y-%m-%d')):
        result = self.collection_price.aggregate([
            {
                '$match': {
                    'date': date,
                }
            },
            {
                '$group': {
                    '_id': "$house_id",
                    '单价': { '$avg': "$单价" },
                }
            },
            {
                '$lookup':
                    {
                        'from': 'house_detail',
                        'localField': '_id',
                        'foreignField': '_id',
                        'as': 'detail'
                    }
            },
            {
                '$group': {
                    '_id': "$detail.小区名称",
                    'count': { '$sum': 1 },
                    'avg': { '$avg': "$单价" }
                }
            },
            { "$match": {"count": { '$gte': 20} }},
            # { "$match": {"_id": "建业"}},
            { "$sort": { "avg": -1 } },
        ])
        for i in result:
            print(i)

    def rise_and_fall(self, startDate = datetime.strptime('2019-01-01', '%Y-%m-%d'), endDate = datetime.strptime(str(date.today()), '%Y-%m-%d')):
        '''
        涨跌数据
        '''
        group_price = self.collection_price.aggregate([
            {
                "$match": {
                    '$or': [
                        {'date': startDate},
                        {'date': endDate}
                    ]
                }
            },
            { "$sort": {'date':-1} },
            {
                '$group': {
                    '_id': {
                        "house_id": "$house_id"
                    },
                    'count': {'$sum': 1},
                    'data': {'$push': {
                        "price":"$单价",
                        "date":"$date"
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
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "rising":"$isRising",
                    },
                    "count": {"$sum":1}
                }
            }
        ])
        for item in group_price:
            print(item)

    def avg_orderby_price(self):  # 日期均价，价格排序
        result = self.collection_price.aggregate([
            {
                '$group': {
                    '_id': {
                        "日期": "$date"
                    },
                    'count': {'$sum': 1},
                    'avg': {'$avg': "$单价"}
                }
            },
            {"$sort": {"avg": -1}},
        ])
        for i in result:
            print(i)

    def avg_orderby_date(self):  # 日期均价，日期排序
        result = self.collection_price.aggregate([
            {
                '$group': {
                    '_id': {
                        "日期": "$date"
                    },
                    'count': {'$sum': 1},
                    'avg': {'$avg': "$单价"}
                }
            },
            {"$sort": {"_id.日期": -1}},
        ])
        for i in result:
            print(i)

if __name__ == '__main__':
    Analysis().group_by_community(date=datetime.strptime('2019-01-28', '%Y-%m-%d'))
    Analysis().rise_and_fall(startDate=datetime.strptime('2019-01-28', '%Y-%m-%d'), endDate=datetime.strptime('2019-03-01', '%Y-%m-%d'))
    Analysis().avg_orderby_price()
    Analysis().group_by_aera()
