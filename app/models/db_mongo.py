import logging
import pymongo
import datetime
import os
from app.models.leetcode_user import User

mongo_url = os.getenv("MONGODB_URI2", "mongodb://root:example@localhost:27017/")
mongo_db_name = os.getenv("MONGODB_NAME2", "LEET_CODE")

myclient = pymongo.MongoClient(mongo_url)
mydb = myclient[mongo_db_name]


def create_indexes():
    try:
        users_collection = mydb.users
        indexes = ['country_code', 'user_name', 'real_name']
        existed_indexes = list(map(lambda x: x['name'], users_collection.list_indexes()))
        if len(existed_indexes) > len(indexes):
            users_collection.reindex()
        for index in indexes:
            if (index + "_1") not in existed_indexes:
                users_collection.create_index(index)
    except Exception as e:
        logging.error(e, exc_info=True)


def insert_users(users):
    try:
        users_collection = mydb.users
        data = []
        for user in users:
            row = {"global_ranking": user.global_ranking, "ranking": user.rating, "user_name": user.user_name,
                   "real_name": user.real_name, "country_code": user.country_code, "country_name": user.country_name,
                   "page": user.page, "data_region": user.data_region}
            data.append(row)
        return users_collection.insert_many(data)
    except Exception as e:
        logging.error(e, exc_info=True)


def delete_users_by_page(page):
    try:
        return mydb.users.remove({"page": page})
    except Exception as e:
        logging.error(e, exc_info=True)


def get_users(page_size, page_num):
    res = []
    try:
        cursor = mydb.users.find().sort("global_ranking").skip(page_num).limit(page_size)
        users = [x for x in cursor]
        for user in users:
            res.append(User(user['global_ranking'], user['ranking'], user['user_name'], user['real_name'],
                            user['country_code'], user['country_name'], user['page'], user['data_region']))        
    except Exception as e:
        logging.error(e, exc_info=True)
    finally:
        return res


def get_users_by_country(country_code, page_size, page_num):
    res = []
    try:        
        cursor = mydb.users.find({"country_code": country_code}).sort("global_ranking").skip(page_num).limit(page_size)
        users = [x for x in cursor]
        for user in users:
            res.append(User(user['global_ranking'], user['ranking'], user['user_name'], user['real_name'],
                            user['country_code'], user['country_name'], user['page'], user['data_region']))
    except Exception as e:
        logging.error(e, exc_info=True)
    finally:
        return res


def get_users_by_name(user_name, page_size, page_num):
    res = []    
    try:
        query = {"$or": [{"user_name": {"$regex": user_name}}, {"real_name": {"$regex": user_name}}]}
        cursor = mydb.users.find(query).sort("global_ranking").skip(page_num).limit(page_size)
        users = [x for x in cursor]
        for user in users:
            res.append(User(user['global_ranking'], user['ranking'], user['user_name'], user['real_name'],
                            user['country_code'], user['country_name'], user['page'], user['data_region']))
    except Exception as e:
        logging.error(e, exc_info=True)
    finally:
        return res


def get_total_users_count_by_country(country_code):
    try:
        total = mydb.users.find({"country_code": country_code}).count()
        return total
    except Exception as e:
        logging.error(e, exc_info=True)


def get_total_users_count():
    try:
        total = mydb.users.count()
        return total
    except Exception as e:
        logging.error(e, exc_info=True)


def store_last_update(curr_page):
    try:
        date_time_now = datetime.datetime.now()
        date_time_now_str = date_time_now.strftime("%d/%m/%Y %H:%M:%S")
        mydb.updated_user_info.update({"id": 1},
                                      {"id": 1, "last_update_time": date_time_now_str, "last_page": curr_page},
                                      upsert=True)
    except Exception as e:
        logging.error(e, exc_info=True)


def get_last_update():
    try:
        date_time_now = datetime.datetime.now()
        date_time_now_str = date_time_now.strftime("%d/%m/%Y %H:%M:%S")
        rows = mydb.updated_user_info.find({"id": 1})
        for row in rows:
            return {"last_update_time": row["last_update_time"], "last_page": row["last_page"]}
        return {"last_update_time": date_time_now_str, "last_page": 1}
    except Exception as e:
        logging.error(e, exc_info=True)
        return {"last_update_time": date_time_now_str, "last_page": 1}
