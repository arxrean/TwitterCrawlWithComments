import os
import glob
import json
import pickle
import tweepy

CONSUMER_KEY = 'upbdO5eE5vISNg5fKCvnwUss2'
CONSUMER_SECRET = 'z5rfXzMcyUfNQK68v2TosYDCNaLKH08PJhrwNrrIN4pPfnSNZ1'
OAUTH_TOKEN = '1247263867954176000-Q8DwLfD6Al5Jx3ibc4q44d1LxNtbtW'
OAUTH_TOKEN_SECRET = '7C8CsC6RcBlj66b9eitFDHlh5yN75b21fXPqAwajt2kYe'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)


def crawl(line):
	ids, label = line.strip().split(' ')
	all_ids = [ids]
	ids = [ids]
	while ids:
		for id in ids:
			os.system('scrapy crawl twitter_tree -a tweet_id={}'.format(id))

		ids = []
		pkls = glob.glob('*.pkl')
		for p in pkls:
			with open(p, 'rb') as handle:
				pkl = pickle.load(handle)
			for item in pkl:
				item, reply = item.split('-')
				reply = 0 if reply == '' or reply == '0' else int(reply)
				item = item.split('/')[-1]
				if item in all_ids:
					continue
				if item.isdigit():
					all_ids.append(item)
					try:
						tweet = api.get_status(item, tweet_mode='extended')._json
					except:
						continue
					tweet['reply_count'] = reply
					with open('{}.json'.format(item), 'w') as f:
						json.dump(tweet, f)
					if reply > 0:
						ids.append(item)
			os.remove(p)


if __name__ == '__main__':
	for line in open('twitter_ids.txt', 'r').readlines():
		id, label = line.strip().split(' ')
		if os.path.exists('./result/{}_{}'.format(id, label)):
			continue
		if not id.isdigit():
			continue

		crawl(line)
		os.mkdir('./result/{}_{}'.format(id, label))
		os.mkdir('./result/{}_{}/comments'.format(id, label))
		os.system('mv *.json ./result/{}_{}/comments'.format(id, label))

		tweet = api.get_status(id, tweet_mode='extended')._json
		with open('{}.json'.format(id), 'w') as f:
			json.dump(tweet, f)
		os.system('mv {}.json ./result/{}_{}'.format(id, id, label))
