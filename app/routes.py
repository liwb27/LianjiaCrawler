import datetime
from flask import render_template, request, jsonify
from app import app
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.lianjia
c_detail = db.house_detail
c_price = db.house_price
c_meta_day = db.house_meta_day

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/house/<int:id>')
def house_detail(id):
    house = c_detail.find_one({'_id':id})
    if house == None:
        return render_template('house_not_found.html', title='Detail')
    else:
        return render_template('house.html', title='Detail', house=house)

@app.route('/api/meta_day', methods=['GET'])
def api_meta_day():
    today = datetime.datetime.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    day = request.args.get('day', today.day, type=int)
    meta_data = c_meta_day.find_one({
        'year': year,
        'month': month,
        'day': day,    
    })
    if meta_data != None:
        meta_data.pop('_id')
    return jsonify(meta_data)

@app.route('/api/price', methods=['GET'])
def api_price():
    id = request.args.get('id', None, type=int)
    items = c_price.find({'house_id':id})
    data = []
    for item in items:
        for detail in item['detail']:
            data.append({
                'date': str(item['year'])+'/'+str(item['month'])+'/'+str(detail['day']),
                'price': detail['单价'],
                'total': detail['总价'],
            })

    return jsonify(data)