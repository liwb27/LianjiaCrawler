# LianjiaCrawler
## 文件说明
> main.py 主程序，包含以下控制参数：<br>
>> is_offline：控制是否在线爬取房源url列表，离线模式下读取本地house_list.txt中存储的房源url列表，在线模式下读取本地列表后与在线抓取的列表合并。<br>
>> is_update_db：在数据库中发现相同ID的房源后的操作，True：更新数据库，False：跳过该房源<br>
>> mongo_conn：mongodb数据库连接<br>
>> url：链家网站地址，更改次地址以爬取不同的城市<br>

> houselist.py 
>> 爬取房源url列表<br>

> housedetail.py 
>> 从房源url中爬取房源详细信息<br>

## 运行环境
> Python 3.6

## 依赖库
> BeautifulSoup
>> 安装：pip install bs4

> pymongo
>> 安装：pip install pymongo
