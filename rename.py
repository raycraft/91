import redis, os

file_list = os.listdir("g:/1")
client = redis.StrictRedis("localhost", 6379)
key_list = client.hkeys("91_detail")	
for a in file_list:
	ok = False
	for k in key_list:
		key = k.decode("utf-8")
		if a == key:

			try:
				value = client.hget("91_detail", key).decode("utf-8").replace("\n", "").replace(" ", "").replace("-Chinesehomemadevideo", "") \
				.replace(":", "").replace("*", "").replace("?", "")
				# .replace("\"", "").replace("\/", "").replace("\\\", ")
				froma = "g:/1/" + str(key)
				to = "g:/1/" + value + ".mp4"
				os.rename(froma, to)
				print("rename file ", key, " to ", froma, to)
				ok = True
			except:
				continue

		if ok:
			break;

