# Project

Crawl the content of tweets without limitation.

### Environment

- Mac OS
- Chrome (others may be also fine)
- Chromedriver (may need to be redownloaded from [here](https://chromedriver.chromium.org/downloads) depending on the version of your browser)

### Crawl Images from Single Tweet

```
scrapy crawl twitter_single -a tweet_id=1273569944081510400
```

You can modify `get_single_tweet` function in `./twitter_conversation_crawler/spiders/twitter_single.py` to change the save path.

### Crawl Images from Single Tweet Recursively

It crawls contens from a tweet recursively with its comments. The content includes text and image if the post or the comment has. You can add more ids in `twitter_ids.txt`. The results are in the `result` folder.

```shell
python pipeline.py
```

