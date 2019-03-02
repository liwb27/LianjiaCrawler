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
// 区域均价
db.house_detail.explain('executionStats').aggregate([
    {
        "$unwind": "$价格"
    },
    {
        "$match": {
            "价格.date": new Date("2019-01-02")
        }
    },
    {
        $group: {
            _id: "$小区名称",
            count: { $sum: 1 },
            avg: { $avg: "$价格.单价" }
        }
    },
    { "$sort": { "count": -1 } },
]);

//按日期均值
db.house_detail.aggregate([
    {
        "$unwind": "$价格"
    },
    {
        $group: {
            _id: "$价格.date",
            count: { $sum: 1 },
            avg: { $avg: "$价格.单价" }
        }
    },
    { "$sort": { "_id": -1 } },
]);


db.house_detail.aggregate([
    {
        "$unwind": "$价格"
    },
    {
        $group: {
            _id: {
                "区域":"$小区名称",
                "日期":"$价格.date"
            },
            count: { $sum: 1 },
            avg: { $avg: "$价格.单价" }
        }
    },
    { "$sort": { "avg": -1 } },
]);


db.house_detail.explain().aggregate([
    {
        "$unwind": "$价格"
    },
    {
        $group: {
            _id: {
                "区域":"$小区名称",
                "日期":"$价格.date"
            },
            count: { $sum: 1 },
            avg: { $avg: "$价格.单价" }
        }
    },
    { "$sort": { "avg": -1 } },
]);