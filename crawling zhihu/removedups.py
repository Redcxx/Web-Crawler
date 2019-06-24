import getpass, pymongo

database = 'zhihu'
collection = 'new_answers'
key = '$' + 'target.excerpt'

username = input('Enter your Mongodb username: ').strip()
password = getpass.getpass(prompt='Enter your Mongodb password: ')
head="mongodb+srv://"
tail= "@dbcluster-iaoeo.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(head + username + ":" + password + tail)
db = client[database]
pipline = [
    {"$group": {"_id": key, "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
    {"$match": {"count": { "$gte": 2 }}}
]
cursor = db[collection].aggregate(pipline)

response = []
for doc in cursor:
    del doc["unique_ids"][0]
    for id in doc["unique_ids"]:
        response.append(id)
db[collection].delete_many({"_id": {"$in": response}})
print('done', len(response))
