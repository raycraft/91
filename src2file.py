import redis, math, common

c = redis.StrictRedis("localhost", 6379)
lst = c.lrange(common.SRC, 0, -1)

total = len(lst)
count = math.floor(total / 1000) + 1 # 比如 100005个，需要4个文件，每个文件1000个，最后一个文件5个

for i in range(1, count + 1): 
	s = ""
	for a in lst[(i - 1) * 1000 : i * 1000]:
		src = a.decode("utf-8")
		if src != "None":
			s += src + "\n"
			c.lrem(common.SRC, 1, src)
			# print("remove from redis ", src)

	with open(common.TORRENT + "/" + str(i) + ".txt", 'a') as f:
		f.write(s)
	print("writing file ", i)
