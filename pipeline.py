import os
import glob
import json
import pickle
import tweepy

# CONSUMER_KEY = 'upbdO5eE5vISNg5fKCvnwUss2'
# CONSUMER_SECRET = 'z5rfXzMcyUfNQK68v2TosYDCNaLKH08PJhrwNrrIN4pPfnSNZ1'
# OAUTH_TOKEN = '1247263867954176000-Q8DwLfD6Al5Jx3ibc4q44d1LxNtbtW'
# OAUTH_TOKEN_SECRET = '7C8CsC6RcBlj66b9eitFDHlh5yN75b21fXPqAwajt2kYe'

CONSUMER_KEY = 'mtfix8NkJPnA9TZ8n8CiO5Myo'
CONSUMER_SECRET = 'NLhn55azqIiBHwOAJIvQrYMVgguv6SZ0mpItYvHDMrbXR7Vr3n'
OAUTH_TOKEN = '1012412550598791169-IGnxpNu0YDTzCI2b74uafNI9fxHjuD'
OAUTH_TOKEN_SECRET = 'd1fknMVuuJAKdHrBoY9v8gtOmmNLuEzLFRZf5YfDTQ4cA'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)


def crawl(line):
	ids = line.strip()
	all_ids = [ids]
	all_reply = [-1]
	all_has_img = [1]
	ids = [ids]
	while ids:
		for id in ids:
			os.system('scrapy crawl twitter_recursion -a tweet_id={}'.format(id))

		ids = []
		pkls = glob.glob('./result/*.pkl'.format(line.strip()))
		for p in pkls:
			with open(p, 'rb') as handle:
				pkl = pickle.load(handle)
			for item in pkl:
				item, reply, has_img = item.split('-')
				if 'K' in reply:
					reply = reply.replace('K', '000')
				reply = 0 if reply == '' or reply == '0' else int(reply)
				item = item.split('/')[-1]
				if item in all_ids:
					continue
				if item.isdigit():
					all_ids.append(item)
					all_reply.append(reply)
					all_has_img.append(has_img)
					if reply > 0:
						ids.append(item)

			os.remove(p)

	all_reply[0] = len(all_ids)-1
	return all_ids, all_reply, all_has_img


if __name__ == '__main__':
	if not os.path.exists('./result'):
		os.mkdir('./result')

	for line in open('twitter_ids.txt', 'r').readlines():
		id = line.strip()
		if os.path.exists('./result/{}'.format(id)):
			continue

		os.mkdir('./result/{}'.format(id))

		all_comment_ids, all_reply_num, all_has_img = crawl(id)
		for id2 in all_comment_ids:
			os.mkdir('./result/{}/{}'.format(id, id2))

		for i, _id in enumerate(all_comment_ids):
			if _id == id:	
				tweet = api.get_status(_id, tweet_mode='extended')._json
			else:
				try:
					tweet = api.get_status(_id, tweet_mode='extended')._json
				except:
					continue

			tweet['reply'] = all_reply_num[i]

			with open('./result/{}/{}/{}.json'.format(id, _id, _id), 'w') as f:
				json.dump(tweet, f)

			if all_has_img[i] == 1:
				os.system('scrapy crawl twitter_image -a tweet_id={}'.format(_id))
				os.system('mv ./{}-* ./result/{}/{}'.format(_id, _id, _id))
