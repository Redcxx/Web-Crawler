import pymongo
import getpass

database = 'zhihu'
collection = 'answers'
username = input('Enter your Mongodb username: ').strip()
password = getpass.getpass(prompt='Enter your Mongodb password: ')
client = pymongo.MongoClient("mongodb+srv://" + username + ":" + password + "@dbcluster-iaoeo.mongodb.net/test?retryWrites=true&w=majority")
db = client[database]

db.answers.aggregate([ { '$match': {} }, { '$out': "answers_backup" } ])
