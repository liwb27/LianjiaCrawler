use lianjia;
// 房屋数量最多的小区
db.house_detail.aggregate([{ $group: { _id: "$小区名称", count: { $sum: 1 } } }, { "$sort": { "count": -1 } },]);
// 按区间聚合房屋面积
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
            "avg": { "$avg": "$建筑面积" }
        }
    }
])
// 区域均价
db.house_detail.aggregate([
    {
        "$unwind": "$单价"
    },
    {
        "$match": {
            "单价.date": '2018-12-15'
        }
    },
    {
        $group: {
            _id: "$所在区域",
            count: { $sum: 1 },
            avg: { $avg: "$单价.单价" }
        }
    },
    { "$sort": { "avg": -1 } },
]);