# -*- coding: utf-8 -*-

import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from util.limitar import limit_request

# web app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQL_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# database engine
engine = sqlalchemy.create_engine(os.getenv('SQL_URI'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
db = SQLAlchemy()

with app.app_context():
    db.init_app(app)

@app.route('/')
def index():
    if limit_request(request.remote_addr):
        return jsonify({"message": "Too Many Requests", "status": 429})

    return 'Welcome to EQ Works 😎'


@app.route('/events/hourly')
def events_hourly():
    if limit_request(request.remote_addr):
        return jsonify({"message": "Too Many Requests", "status": 429})

    return queryHelper('''
        SELECT date, hour, events
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/events/daily')
def events_daily():
    if limit_request(request.remote_addr):
        return jsonify({"message": "Too Many Requests", "status": 429})

    return queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')


@app.route('/stats/hourly')
def stats_hourly():
    if limit_request(request.remote_addr):
        return jsonify({"message": "Too Many Requests", "status": 429})

    return queryHelper('''
        SELECT date, hour, impressions, clicks, revenue
        FROM public.hourly_stats
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/stats/daily')
def stats_daily():
    if limit_request(request.remote_addr):
        return jsonify({"message": "Too Many Requests", "status": 429})

    return queryHelper('''
        SELECT date,
            SUM(impressions) AS impressions,
            SUM(clicks) AS clicks,
            SUM(revenue) AS revenue
        FROM public.hourly_stats
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')

@app.route('/poi')
def poi():
    if limit_request(request.remote_addr):
        return {"message": "Too Many Requests"}, 429

    return queryHelper('''
        SELECT *
        FROM public.poi;
    ''')

def queryHelper(query):
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return jsonify([dict(row.items()) for row in result])
