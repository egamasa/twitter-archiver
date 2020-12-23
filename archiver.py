# coding: utf-8

import os
import json
import config
import datetime
import boto3
import time
from datetime import timedelta, timezone
from requests_oauthlib import OAuth1Session
from logger import logger


CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET

MAX_REQUEST_TIMES = 10
MAX_RETRY_TIMES = 3
RETRY_WAIT_TIME = 30

API_URL = {
    'timeline': "https://api.twitter.com/1.1/statuses/user_timeline.json",
    'favorite': "https://api.twitter.com/1.1/favorites/list.json",
    'limit': "https://api.twitter.com/1.1/application/rate_limit_status.json"
}

twitter = OAuth1Session(CK, CS, AT, ATS)


def datetime_parse(dt: str) -> datetime:
    parsed_dt = datetime.datetime.strptime(dt, '%a %b %d %H:%M:%S %z %Y')
    return parsed_dt


def filter_term():
    JST = timezone(timedelta(hours=+9), 'JST')
    dt_now = datetime.datetime.now(JST)
    d_start = (dt_now - datetime.timedelta(days=1)).date()
    d_end = dt_now.date()
    t_sep = datetime.time(hour=0, minute=0, second=0)
    dt_start = datetime.datetime.combine(d_start, t_sep, JST)
    dt_end = datetime.datetime.combine(d_end, t_sep, JST)
    return dt_start, dt_end


def timeline_params(max_id: str = 0) -> dict:
    params = {
        'count': 100,
        'trim_user': False,
        'exclude_replies': False,
        'include_rts': True,
        'tweet_mode': 'extended'
    }
    if max_id != 0:
        params['max_id'] = max_id
    return params


def favorite_params(max_id: str = 0) -> dict:
    params = {
        'count': 100,
        'tweet_mode': 'extended'
    }
    if max_id != 0:
        params['max_id'] = max_id
    return params


def api(url: str, params: dict = {}) -> dict:
    retry = 0
    for i in range(MAX_RETRY_TIMES + 1):
        res = twitter.get(url, params=params)
        if res.status_code == 200:
            return json.loads(res.text)
        elif retry > MAX_RETRY_TIMES:
            raise Exception('[TwitterArchiver] Twitter API: Reached max retry times')
        elif res.status_code == 503:
            retry = retry + 1
            time.sleep(RETRY_WAIT_TIME)
        elif res.status_code == 429:
            raise Exception('[TwitterArchiver] Twitter API: Too Many Requests (429)')
        else:
            raise Exception('[TwitterArchiver] Twitter API: Error')


def get_request(endpoint: str, dt_start: datetime, dt_end: datetime) -> list:
    last_id = 0
    tweets = []

    for i in range(MAX_REQUEST_TIMES):
        params = {}
        if endpoint == 'timeline':
            params = timeline_params(last_id)
        elif endpoint == 'favorite':
            params = favorite_params(last_id)
        tweets_list = api(API_URL[endpoint], params)

        for tweet in tweets_list:
            dt_tweet = datetime_parse(tweet['created_at'])
            if dt_tweet < dt_start:
                break
            elif dt_end <= dt_tweet:
                continue
            elif last_id == tweet['id']:
                continue
            else:
                tweets.append(tweet)
        last_id = tweets_list[-1]['id']
    return tweets


def save_path(dt: datetime) -> str:
    y = dt.strftime('%Y')
    m = dt.strftime('%m')
    d = dt.strftime('%d')
    pattern = {'yyyy': y, 'mm': m, 'dd': d}
    path = config.SAVE_PATH.format(**pattern)
    name = config.SAVE_NAME.format(**pattern)
    return path, name


def save_to_s3(data: dict, name: str):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=config.ACCESS_KEY_ID,
        aws_secret_access_key=config.SECRET_ACCESS_KEY,
        # region_name=config.REGION_NAME,
        endpoint_url=config.ENDPOINT_URL,
    )
    obj = s3.Object(config.BUCKET_NAME, name)
    res = obj.put(Body=json.dumps(data))
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f"[TwitterArchiver] Saved to S3: {config.BUCKET_NAME}/{name}")
        return
    else:
        raise Exception('[TwitterArchiver] Save to S3: Error')


def main(event={}, context={}):
    dt_start, dt_end = filter_term()
    path, name = save_path(dt_start)

    tweets = get_request('timeline', dt_start, dt_end)
    favs = get_request('favorite', dt_start, dt_end)
    data = {
        'timeline': tweets,
        'favorites': favs,
    }

    if config.SAVE_TO_S3:
        save_to_s3(data, os.path.join(path, name))
    else:
        with open(name, 'w') as outfile:
            json.dump(data, outfile)
            logger.info(f"[TwitterArchiver] Saved to file: {name}")


# For debug on local
main()
