from flask import Blueprint, render_template, send_from_directory, request, redirect
from flask_paginate import Pagination, get_page_args
from app.models import db_mongo
import os
from app.models.cache import cache

app_ctr = Blueprint('app_ctr', __name__)


@app_ctr.route('/')
def index():
    last_updated_format = cache.get('last_updated_format')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = db_mongo.get_total_users_count()
    pagination_users = db_mongo.get_users(per_page, offset)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html', users=pagination_users, page=page, per_page=per_page, pagination=pagination,
                           last_updated=last_updated_format)


@app_ctr.route('/country/<country_name>')
def search_by_country(country_name):
    last_updated_format = cache.get('last_updated_format')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = db_mongo.get_total_users_count_by_country(country_name)
    pagination_users = db_mongo.get_users_by_country(country_name, per_page, offset)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html', users=pagination_users, page=page, per_page=per_page, pagination=pagination,
                           last_updated=last_updated_format)


@app_ctr.route('/user', methods=['POST'])
def search_by_user():
    last_updated_format = cache.get('last_updated_format')
    user_name = request.form.get("user-search")
    if not user_name:
        return redirect('/')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination_users = db_mongo.get_users_by_name(user_name, per_page, offset)
    total = len(pagination_users)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html', users=pagination_users, page=page, per_page=per_page, pagination=pagination,
                           last_updated=last_updated_format)


@app_ctr.context_processor
def my_utility_processor():
    def format_rate(rate):
        return format(float(rate), '.2f')
    return dict(format_rate=format_rate)