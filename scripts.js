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
                    { "$lt": ["$建筑面积", 60] },
                    "0-60",
                    {
                        "$cond": [
                            { "$lt": ["$建筑面积", 80] },
                            "60-80",
                            {
                                "$cond": [
                                    { "$lt": ["$建筑面积", 100] },
                                    "80-100",
                                    {
                                        "$cond": [
                                            { "$lt": ["$建筑面积", 120] },
                                            "100-120",
                                            {
                                                "$cond": [
                                                    { "$lt": ["$建筑面积", 140] },
                                                    "120-140",
                                                    {
                                                        "$cond": [
                                                            { "$lt": ["$建筑面积", 160] },
                                                            "140-160",
                                                            "160+"
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
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
                            6
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

// 当日均价
db.house_price.aggregate([
    { $unwind : "$detail" },    
    {
        $match: {
            'year':2019,
            'month':11,
            'detail.day':20,            
        }
    },
    {
        $group: {
            _id: null,
            count: { $sum: 1 },
            avg: { $avg: "$detail.单价" }
        }
    },
]);


// 区域均价
// db.house_detail.explain('executionStats').aggregate([
db.house_price.aggregate([
    { $unwind : "$detail" },    
    {
        $match: {
            'year':2018,
            'month':12,
            'detail.day':30,            
        }
    },
    {
        $lookup:
            {
                from: 'house_detail',
                localField: 'house_id',
                foreignField: '_id',
                as: 'house_detail'
            }
    },
    {
        $replaceRoot: { newRoot: { $mergeObjects: [ { $arrayElemAt: [ "$house_detail", 0 ] }, "$$ROOT" ] } }
    },
    { $project: { house_detail: 0 } },
    {
        $group: {
            _id: "$house_detail.小区名称",
            count: { $sum: 1 },
            avg: { $avg: "$detail.单价" }
        }
    },
    { "$match": {"count": { $gte: 70} }},
    { "$sort": { "avg": -1 } },
    { "$limit": 10 },
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