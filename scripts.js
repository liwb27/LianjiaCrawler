use lianjia;
// 房屋数量最多的小区
db.house_detail.aggregate([{ $group: { _id: "$小区名称", count: { $sum: 1 } } }, { "$sort": { "count": -1 } },]);
// 按区间聚合房屋面积
var nums = db.house_detail.count();
db.house_detail.aggregate([
    {
        "$group": {
            "_id": {
                "$cond": [
                    { "$lt": ["$建筑面积", 100] },
                    "0-100",
                    {
                        "$cond": [
                            { "$lt": ["$建筑面积", 150] },
                            "100-150",
                            "150+"
                        ]
                    }
                ]
            },
            "count": { "$sum": 1 },
            "avg": { "$avg": "$建筑面积" },
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
                                "$multiply": [{ "$divide": ["$count", { "$literal": nums }] }, 100]
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

//两表合并
db.house_detail.aggregate([    
    {
        $lookup:
            {
                from: 'house_price',
                localField: '_id',
                foreignField: 'house_id',
                as: 'price_data'
            }
    },
])

// 区域均价
// db.house_detail.explain('executionStats').aggregate([
db.house_price.aggregate([
    {
        $match: {
            'date': new Date("2019-03-01"),
        }
    },
    {
        $group: {
            _id: "$house_id",
            '单价': { $avg: "$单价" },
        }
    },
    {
        $lookup:
            {
                from: 'house_detail',
                localField: '_id',
                foreignField: '_id',
                as: 'detail'
            }
    },
    {
        $group: {
            _id: "$detail.小区名称",
            count: { $sum: 1 },
            avg: { $avg: "$单价" }
        }
    },
    { "$match": {"count": { $gte: 70} }},
    { "$sort": { "avg": -1 } },
]);

//按日期均值
db.house_price.aggregate([
    {
        $group: {
            _id: {
                "日期":"$date"
            },
            count: { $sum: 1 },
            avg: {$avg: "$单价"}
        }
    },
    { "$sort": { "avg": 1 } },
]);

db.house_price.aggregate([
    {
        $group: {
            _id: {
                "日期":"$date"
            },
            count: { $sum: 1 },
            avg: {$avg: "$单价"}
        }
    },
    { "$sort": { "_id": -1 } },
]);

// 涨跌统计
db.house_price.aggregate([
    {
        "$match": {
            '$or': [
                {'date': new Date("2019-01-01")},
                {'date': new Date("2019-03-01")}
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
            'end':  { $arrayElemAt: ["$data.price", 0] },
            'start': { $arrayElemAt: ["$data.price", -1] },
        }
    },
    {
        "$project": {
            "isRising" : {
                "$cond" : {
                    "if": { $gt: [ "$start", "$end" ] },
                    "then": false,
                    "else": true
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