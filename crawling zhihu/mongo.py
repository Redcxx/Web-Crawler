import pymongo

client = pymongo.MongoClient()
db = client['test']
datas = db.student.find()
for data in datas:
    print(data['name'] + " "  + data['age'])



# insert
item = {'name': 'xiao gu', 'age': '19'}
db.student.insert_one(item)
items = [{'name': 'xiao zhao', 'age': '24'}, {'name': 'xiao wu', 'age': '29'}]
db.student.insert_many(items)
data = db.student.find({'name': 'xiao wu'})
print("===========")
for item in data:
    print(item['name'] + " " + item['age'])
