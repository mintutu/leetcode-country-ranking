# -*- encoding: utf-8 -*-
from flask import Flask, render_template, send_from_directory, request, redirect
from flask_paginate import Pagination, get_page_args
import threading
import requests
import os
import json
import time
import datetime
from . import db_mongo
from app.leetcode_user import User
app = Flask(__name__)
app.config.from_pyfile('app.cfg')

MAX_PAGE = int(os.getenv("MAX_PAGE_LEET_CODE", "15"))
SCANNER_ENABLED = os.getenv("SCANNER_ENABLED", "True")

last_updated_format = None

def craw_leetcode(page):
	users = list()
	try:
		data = {"query": "{  globalRanking(page: "+ str(page)  +") {    totalUsers,    userPerPage,    myRank {      ranking,      currentGlobalRanking,      currentRating,      dataRegion,      __typename,    },    rankingNodes {      ranking,      currentRating,      currentGlobalRanking,      dataRegion,      user {        username,      profile {          userSlug,          userAvatar,          countryCode,          countryName,          realName,          __typename,        },        __typename      },      __typename,    },    __typename  }}"}
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
			currrent_ranking = node["currentRating"]
			user_profile = node['user']['profile']      
			user_name = user_profile['userSlug']  
			real_name = user_profile['realName']
			country_code = user_profile['countryCode']
			country_name = user_profile['countryName']			
			user = User(global_ranking, currrent_ranking, user_name, real_name, country_code, country_name, page)
			users.append(user)
	except Exception as e:
		print(e)
	finally:
		return users

def scan_ranking(last_page):	
	for i in range(last_page, MAX_PAGE):
		users = craw_leetcode(i)
		if (len(users) > 0):
			db_mongo.delete_users_by_page(i)
			result = db_mongo.insert_users(users)
			db_mongo.store_last_update(i)
			print ("Inserted to DB page " + str(i))
			time.sleep(3)

def start_scan():
	global last_updated_format
	while True:
		if SCANNER_ENABLED == 'True':		
			db_mongo.create_indexes()
			last_updated_info = db_mongo.get_last_update()
			last_page = last_updated_info["last_page"]
			last_updated_str = last_updated_info["last_update_time"]
			last_updated = datetime.datetime.strptime(last_updated_str, "%d/%m/%Y %H:%M:%S")		
			last_updated_format = last_updated.strftime("%B %d, %Y")

			diff_date_time = datetime.datetime.now() - last_updated
			if (diff_date_time.days >= 1):
				last_page = 1
			print('Start scan leetcode ranking from page ' + str(last_page))
			scan_ranking(last_page)
			print('Finish scan leetcode ranking')
		#Rescan every day
		time.sleep(60 * 60 * 24)

@app.route('/')
def index():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = db_mongo.get_total_users_count()
    pagination_users = db_mongo.get_users(per_page, offset)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',users=pagination_users,page=page,per_page=per_page,pagination=pagination,last_updated=last_updated_format)

@app.route('/country/<country_name>')
def search_by_country(country_name):
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = db_mongo.get_total_users_count_by_country(country_name)
    pagination_users = db_mongo.get_users_by_country(country_name, per_page, offset)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',users=pagination_users,page=page,per_page=per_page,pagination=pagination,last_updated=last_updated_format)

@app.route('/user',methods = ['POST'])
def search_by_user():
    user_name = request.form.get("user-search")
    if not user_name:
        return redirect('/')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')    
    pagination_users = db_mongo.get_users_by_name(user_name, per_page, offset)
    total = len(pagination_users)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',users=pagination_users,page=page,per_page=per_page,pagination=pagination,last_updated=last_updated_format)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

def ping():
	try:
		while True:
			time.sleep(60 * 15)
			requests.get("https://leetcode-country-ranking.herokuapp.com/")	
	except Exception as e:
		print(e)

t1 = threading.Thread(target=start_scan)
t1.start()

t2 = threading.Thread(target=ping)
t2.start()