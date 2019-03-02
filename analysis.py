from pymongo import MongoClient
from datetime import datetime, date
# todo: '价格'array随时间增长，过大时需要将其拆分成单独collection


class Analysis(object):
    client = MongoClient('mongodb://localhost:27017')
    db = client.lianjia
    collection = db.house_detail

    def most_house_in_community(self):  # 房屋数量最多的小区
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
        for i in result:
            print(i)

    # def top_community(self):  # 均价最高小区
    #     result = self.collection.aggregate([
    #         {
    #             "$unwind": "$价格"
    #         },
    #         {
    #             "$match": {
    #                 "价格.date": datetime.strptime(str(date.today()), '%Y-%m-%d')
    #             }
    #         },
    #         {
    #             '$group': {
    #                 '_id': "$小区名称",
    #                 'count': {'$sum': 1},
    #                 'avg': {'$avg': "$价格.单价"}
    #             }
    #         },
    #         {"$sort": {"avg": -1}},
    #         {"$limit": 20}
    #     ])
    #     for i in result:
    #         print(i)

    # def rise_and_fale(self):  # 涨跌数据
    #     zhang = 0
    #     die = 0
    #     zhang_max = -1
    #     die_max = -1
    #     for item in self.collection.find():
    #         price = item['价格']
    #         diff = price[0]['总价'] - price[-1]['总价']
    #         if diff != 0:
    #             if diff < 0:
    #                 zhang += 1
    #                 if -diff > zhang_max:
    #                     zhang_max = -diff
    #                     zhang_max_id = item['_id']
    #                 print('+++', item['_id'])
    #             else:
    #                 die += 1
    #                 if diff > die_max:
    #                     die_max = diff
    #                     die_max_id = item['_id']
    #                 print('---', item['_id'])
    #     print('涨:{0}, 跌:{1}'.format(zhang, die))
    #     print('涨max:{0}--{1}, 跌max:{2}--{3}'.format(zhang_max,
    #                                                 zhang_max_id, die_max, die_max_id))

    # def avg_orderby_date(self):  # 日期均价
    #     result = self.collection.aggregate([
    #         {
    #             "$unwind": "$价格"
    #         },
    #         {
    #             '$group': {
    #                 '_id': "$价格.date",
    #                 'count': {'$sum': 1},
    #                 'avg': {'$avg': "$价格.单价"}
    #             }
    #         },
    #     ])
    #     data = [i for i in result if i['count'] > 40000]
    #     data.sort(key=lambda param: param['_id'])
    #     for i in data:
    #         print(i)

if __name__ == '__main__':
    Analysis().group_by_aera()