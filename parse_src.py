import requests, re, redis, redisutil, time, random
from pyquery import PyQuery as pq 
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import threading
import common

# 将列表页插入redis
def parse(url, c):
    html = common.visit1(url)
    if html == "error":
        redisutil.add(url, "parse_error")
        print("parsing url ", url, " has some errors")
        return
    d = pq(html)
    src = d("video").find("source").attr("src")
    title = d("head").find("title").html()
   	# 解析其他信息，时长，名字等
    if src != None:
    	print( threading.current_thread().name,  " insert into redis ", src)
    	c.lrem(common.KEY, 1, url)  # KEY 存储即将解析的url, VISITED 存储已经访问过并且已经 解析的url
    	c.rpush(common.VISITED, url)
    	c.rpush(common.SRC, src)
    	print(threading.current_thread().name, " 解析了 ", title)
    	if src is not None:
    		name = src.split("?")[0].split("/")[-1]    	
    		c.hset("91_detail", name, title) # 文件名和中文名的对应关系
    else:
    	print(threading.current_thread().name,  src, "解析为None, 插入 redis_error")
    	redisutil.add(src, common.KEY_NONE)

def enter(**kwargs):
    start = kwargs["start"]
    end = kwargs["end"]
    c = redisutil.connect()
    lst = c.lrange(common.KEY, int(start), int(end))

    for a in lst:
         print(threading.current_thread().name,  " parsing url ", a)
         parse(a, c)
         time.sleep(0.1)
    with open(common.PARSE_LOG, "a") as f:
        f.write(threading.current_thread().name + " 已经解析完毕.\n")

def start():
    thread_list = []
    total = redisutil.total(common.KEY   )
    page_size = 0
    thread_total = 5

    if total <= 5:
    	page_size = 1
    	thread_total = total
    else:
    	page_size = total / 5

    for t in range(1, thread_total + 1):
        start = (t - 1) * page_size + 1
        end = t * page_size + 1
        name = "a" + str(t)
        t = threading.Thread(target=enter, name=name, kwargs={"start":start, "end":end})
        thread_list.append(t)

    for t in thread_list:
    	t.start()

    for t in thread_list:
    	t.join()

    print("all thread over")

start()
