import pymongo
import os
from pymongo import IndexModel, ASCENDING, DESCENDING
from app.leetcode_user import User

mongo_url = os.environ["MONGODB_URI"]
mongo_db_name = os.environ["MONGODB_NAME"]
#Local "mongodb://root:example@localhost:27017/"
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient[mongo_db_name]

def create_indexes():
    try:
        users_collection = mydb.users
        index = 'country_code'
        if 'country_code_1' in map(lambda x: x['name'], users_collection.list_indexes()):
            users_collection.reindex(index)
        else:
            users_collection.create_index(index)
    except Exception as e:
        print(e)

def insert_users(users):
    try:
        users_collection = mydb.users
        data = []
        for user in users:
            row = {"global_ranking": user.global_ranking, "ranking": user.ranking, "user_name": user.user_name, "real_name": user.real_name, "country_code": user.country_code, "country_name": user.country_name, "page": user.page}
            data.append(row)
        return users_collection.insert_many(data)
    except Exception as e:
        print(e)

def delete_users_by_page(page):
    try:
        return mydb.users.remove({"page": page})
    except Exception as e:
        print(e)

def get_users(page_size, page_num):
    try:
        res = []
        cursor = mydb.users.find().sort("global_ranking").skip(page_num).limit(page_size)
        users = [x for x in cursor]
        for user in users:
            res.append(User(user['global_ranking'], user['ranking'], user['user_name'], user['real_name'], user['country_code'], user['country_name'], user['page']))
        return res
    except Exception as e:
        print(e)

def get_users_by_country(country_code, page_size, page_num):
    try:
        res = []
        cursor = mydb.users.find({"country_code": country_code}).sort("global_ranking").skip(page_num).limit(page_size)
        users = [x for x in cursor]
        for user in users:
            res.append(User(user['global_ranking'], user['ranking'], user['user_name'], user['real_name'], user['country_code'], user['country_name'], user['page']))
        return res
    except Exception as e:
        print(e)

def get_total_users_count_by_country(country_code):
    try:
        total = mydb.users.find({"country_code": country_code}).count()
        return total
    except Exception as e:
        print(e)

def get_total_users_count():
    try:
        total = mydb.users.count()
        return total
    except Exception as e:
        print(e)