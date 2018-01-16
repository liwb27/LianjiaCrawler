# LianjiaCrawler
## 文件说明

 main.py 主程序，通过控制参数实现不同模式<br>

 settings.py 包含以下控制参数：
> LIANJIA_URL 链家网址，暂时只测试了郑州<br>

> OFFLINE_MODE<br>
>> TRUE:在线爬取房源列表
>> FALSE:使用本地房源列表，忽略BRIEF_MODE=TRUE

> BRIEF_MODE<br>
>> TRUE:不打开房源单独页面，直接从区域页面读取房源简要信息
>> FALSE:打开每个房源url获取更多信息，速度慢

> MONGO_CONN 数据库链接<br>

> IS_UPDATE_DB 找到已存在房源时是否更新数据库<br>

> FILE_AERA_LIST 区域列表文件名<br>

> FILE_HOUSE_LIST 房源列表文件名<br>

> FILE_HOUSE_DELETE_LIST 已删除房源文件名<br>

> FILE_HOUSE_ERROR_LIST 解析错误房源列表<br>

 houselist.py 爬取房源url列表<br>

 housedetail.py 从房源url中爬取房源详细信息<br>

## 运行环境
> Python 3.6

## 依赖库
> BeautifulSoup
> pymongo
> requests
