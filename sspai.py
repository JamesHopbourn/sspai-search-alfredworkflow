import os
import sys
import json
import redis
import requests
from urllib3 import *
disable_warnings()

tagList = os.environ["tagList"].split('\n')
redisClient = redis.Redis(host='localhost', port=6379, db=0)
redisCache = redisClient.get('sspai')

response = []
if redisCache:
    # 如果缓存中有数据，返回缓存的结果
    response = json.loads(redisCache)
else:
    for tag in tagList:
        for i in range(2):
            SSPAI_API_URL = f'https://sspai.com/api/v1/article/tag/page/get?limit=40&offset={i*40}&tag={tag}'
            response.extend(requests.get(SSPAI_API_URL, verify=False).json()['data'])
    # 将查询到的数据缓存到 Redis
    redisClient.setex('sspai', 60*60*24*30, json.dumps(response, ensure_ascii=False))

result = []
for item in response:
    if sys.argv[1].lower() not in item["title"].lower(): 
        continue
    article = {
        "title": item["title"],
        "subtitle": item["summary"],
        "arg": f"https://sspai.com/post/{item['id']}",
        "autocomplete": item["title"],
        "icon": {
            "path": "icon.png"
        }
    }
    result.append(article)
alfredJSON = json.dumps({"items": result}, indent=2, ensure_ascii=False)
sys.stdout.write(alfredJSON)