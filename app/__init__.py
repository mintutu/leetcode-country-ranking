# -*- encoding: utf-8 -*-
from flask import Flask, render_template, send_from_directory
from flask_paginate import Pagination, get_page_args
from datetime import datetime
import threading
import requests
import os
from urllib import parse
import json
import time
from . import db_mongo
from app.leetcode_user import User
app = Flask(__name__)
app.config.from_pyfile('app.cfg')
MAX_PAGE = 10

def craw_leetcode(page):
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
		users = []
		for node in rankingNodes:
			global_ranking = node["currentGlobalRanking"]
			currrent_ranking = node["currentRating"]
			user_profile = node['user']['profile']      
			user_name = user_profile['userSlug']  
			real_name = user_profile['realName']
			country_code = user_profile['countryCode']
			country_name = user_profile['countryName']
			user = User(global_ranking, currrent_ranking, user_name, real_name, country_code, country_name)
			users.append(user)
		return users
	except Exception as e:
		print(e)
		return None

def scan_ranking():	
	for i in range(1,MAX_PAGE):
		users = craw_leetcode(i)
		result = db_mongo.insert_users(users)
		print (result)
		time.sleep(3)

def start_scan():
	while True:
		print('Start scan leetcode ranking')
		delay_scan = int(os.environ["DELAY_SCAN"])	#delay in minutes
		scan_ranking()
		print('Finish scan leetcode ranking')
		time.sleep(60 * delay_scan)

@app.route('/home')
def homepage():
    last_rates_thb = db_postgre.getLatestRate('supperrich_exchange', 20)  
    data_thb = []
    for rate in last_rates_thb:
    	row = []
    	row.append(rate.cbuy)
    	row.append(rate.csell)
    	row.append(rate.dateTime)
    	data_thb.append(row)

    last_rates_vnd = db_postgre.getLatestRate('tygiado', 10)		
    data_vnd = []
    for rate in last_rates_vnd:
    	row = []
    	row.append(rate.cbuy)
    	row.append(rate.csell)
    	row.append(rate.dateTime)
    	data_vnd.append(row)
    one_baht_vnd = "%.2f" % (data_vnd[0][0] / data_thb[0][1])
    return render_template('result.html', one_baht_vnd=one_baht_vnd, result_vnd=data_vnd, result_thb=data_thb)

@app.route('/')
def index():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = db_mongo.get_total_users_count()
    pagination_users = db_mongo.get_users(per_page, offset)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',users=pagination_users,page=page,per_page=per_page,pagination=pagination)

@app.route('/country/<country_name>')
def search_by_country(country_name):
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = db_mongo.get_total_users_count_by_country(country_name)
    pagination_users = db_mongo.get_users_by_country(country_name, per_page, offset)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',users=pagination_users,page=page,per_page=per_page,pagination=pagination)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
