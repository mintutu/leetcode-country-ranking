import logging
import threading
import requests
import os
import json
import time
import datetime
from app.models import db_mongo
from app.models.leetcode_user import User
from app.models.cache import cache

last_updated_format = None
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def craw_leetcode(page):
    users = list()
    try:
        data = {"query": "{  globalRanking(page: " + str(
            page) + ") {    totalUsers,    userPerPage,    myRank {      ranking,      currentGlobalRanking,      currentRating,      dataRegion,      __typename,    },    rankingNodes {      ranking,      currentRating,      currentGlobalRanking,      dataRegion,      user {        username,      profile {          userSlug,          userAvatar,          countryCode,          countryName,          realName,          __typename,        },        __typename      },      __typename,    },    __typename  }}"}
        result = requests.post("https://leetcode.com/graphql",
                               json=data,
                               headers={
                                   "accept": "*/*",
                                   "accept-language": "en-US,en;q=0.9,vi;q=0.8",
                                   "authority": "leetcode.com",
                                   "content-type": "application/json; charset=utf8",
                                   "origin": "https://leetcode.com",
                                   "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
                               })
        json_result = json.loads(result.text)
        rankingNodes = json_result['data']['globalRanking']['rankingNodes']
        for node in rankingNodes:
            global_ranking = node["currentGlobalRanking"]
            currrent_rating = node["currentRating"]
            data_region = node["dataRegion"]
            user_profile = node['user']['profile']
            user_name = user_profile['userSlug']
            real_name = user_profile['realName']
            country_code = user_profile['countryCode']
            country_name = user_profile['countryName']
            user = User(global_ranking, currrent_rating, user_name, real_name, country_code, country_name, page, data_region)
            users.append(user)
    except Exception as e:
        logging.error(e, exc_info=True)
    finally:
        return users


def scan_ranking(mongo_db, last_page):
    MAX_PAGE = int(os.getenv("MAX_PAGE_LEET_CODE", "15"))
    for i in range(last_page, MAX_PAGE+1):
        users = craw_leetcode(i)
        if len(users) > 0:
            db_mongo.delete_users_by_page(mongo_db, i)
            db_mongo.insert_users(mongo_db, users)
            db_mongo.store_last_update(mongo_db, i)
            logging.info("Inserted to DB page {}".format(i))
            time.sleep(1)


def start_scan():    
    while True:
        scanner_enabled = os.getenv("SCANNER_ENABLED", "True")
        if scanner_enabled == 'True':
            mongo_client = db_mongo.get_mongo_client()
            mongo_db = db_mongo.get_mongo_db(mongo_client)
            last_updated_info = db_mongo.get_last_update(mongo_db)      
            last_page = last_updated_info["last_page"]
            last_updated_str = last_updated_info["last_update_time"]
            logging.info('Last page was scanned {} at {}'.format(last_page,last_updated_str))            
            last_updated = datetime.datetime.strptime(last_updated_str, "%d/%m/%Y %H:%M:%S")
            cache.set('last_updated_format', last_updated.strftime("%B %d, %Y"), timeout=60 * 60 * 24)
            
            diff_date_time = datetime.datetime.now() - last_updated
            logging.info("diff_date_time: {}".format(diff_date_time))
            MAX_PAGE = int(os.getenv("MAX_PAGE_LEET_CODE", "15"))
            if last_page >= MAX_PAGE: 
                if diff_date_time.days <= 1:
                     time.sleep(60)
                     continue
                else:
                    last_page = 1

            logging.info('Start scan leetcode ranking from page {}'.format(last_page))
            scan_ranking(mongo_db, last_page)
            cache.set('last_updated_format', datetime.datetime.now().strftime("%B %d, %Y"), timeout=60 * 60 * 24)            
            logging.info('Finish scan leetcode ranking')
            db_mongo.rebuild_indexes(mongo_db)
            logging.info('Complete rebuild index')
            mongo_client.close()
        # Rescan every day
        time.sleep(5)

#Try to ping website to avoid instance sleeping
def ping():
	try:
		while True:
			time.sleep(60 * 15)
			requests.get("https://leetcode-country-ranking.onrender.com/")	
	except Exception as e:
		logging.error(e, exc_info=True)

def run():    
    t1 = threading.Thread(target=start_scan)
    t1.start()

    # t2 = threading.Thread(target=ping)
    # t2.start()