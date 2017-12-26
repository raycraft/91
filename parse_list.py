import requests, re, redisutil, time, random, threading, os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import common

# 将列表页插入redis
def parseList(url, page):
	# 将当前现场访问的页码写入日志
    with open("log/" + threading.current_thread().name + ".log", "w") as f:
        f.write(str(page))

	# 程序强制退出后下次就不再从第一页开始了，直接从文件中读取
    html = common.visit(url)
    if html == "error" :
        redisutil.add(url, "error")
        print("出现错误了, ", url)
        return
    lst = re.compile(r'href="(.+?)"').findall(html)
    result = []
    for a in lst:
        if "category=mr" in a:
            result.append(a)
    if result is not None and len(result) > 0:
        for a in set(result): 
            if not redisutil.exists(a, common.KEY) and not redisutil.exists(a, common.VISITED):
                redisutil.add(a, common.KEY)    

                print(threading.current_thread().name, " insert into redis ", a)
            else:
                print(threading.current_thread().name, " redis 已经存在，不再访问 ", a)

'''
    线程主方法 
'''
def enter(**kwargs):
    start = kwargs["start"]
    end = kwargs["end"]
    for page in range(start, end):
        url = common.URL + "/v.php?next=watch&page=" + str(page)
        try:
            print(threading.current_thread().name, " 解析 ", page, " 页 ", url)
            # print(threading.current_thread().name, " is invoking this method")
            parseList(url, page)
            # print(threading.current_thread().name, " finished invoking this method")
            time.sleep(random.randint(1,3))
        except RuntimeError:
            print(threading.current_thread().name, " visiting page ", page, " occurs some errors ", RuntimeError.__with_traceback__)
            redisutil.add(url, "91_error")
            continue
    # current thread has finished, log it and we can easily know it 
    with open(common.LOG, "a") as f:
    	f.write("线程" + threading.current_thread().name + " 已经完成抓取 \n")

# 运行方法
def start():
    thread_list = []
    total = common.getNumber()
    thread_total = 5 # 线程总数，默认为5，如果抓取页面小于5，则线程总数就是抓取的页面总数

    if total <= 5:
        page_size = 1
        thread_total = total
    else:
        page_size = int(total / 5) # start 5 thread to visit
    print("start ", thread_total, " thread to get data")


    for i in range(1, thread_total + 1):
        file = "log/" + str(i) + ".log"
        pre = None

        if os.path.exists(file):
            pre = open(file).read()
        
        start = 0

        if pre is None or pre == "":
            start = (i - 1) * page_size + 1
        else:
            start = int(pre)

        end = i * page_size + 1
        name = "a" + str(i)
        t = threading.Thread(target=enter, name=name, kwargs={"start":start,"end":end})
        thread_list.append(t)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()
		
    print("all thread over")

start()
