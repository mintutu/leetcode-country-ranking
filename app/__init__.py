# -*- encoding: utf-8 -*-
from flask import Flask
from flask_compress import Compress
from app.models.cache import cache
from app.controllers.controller import app_ctr
from app import scanner

COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_pyfile('app.cfg')
cache.init_app(app)
app.register_blueprint(app_ctr)
Compress(app)

scanner.run()
