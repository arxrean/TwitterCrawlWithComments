# usage: scrapy crawl twitter_tree -a tweet_id="1021007656511852544" -o result.csv
# this version is collect simplified information


import scrapy
import os
import pdb
import pickle
import urllib.request
from PIL import Image
from scrapy.http import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

class TwitterTree(scrapy.Spider):
    def __init__(self,
                 tweet_id=None):
        self.start_urls = ["https://twitter.com/Nigel21915926/status/%s" % tweet_id]
        self.tweet_id = tweet_id
        self.all_articles = []
        self.first_tweet = False
        self.bad_articles = []
        # remember to set the path of 'geckodriver'
        # if os.path.exists('{}.pkl'.format(tweet_id)):
        #     with open('{}.pkl'.format(tweet_id), 'rb') as f:
        #         self.all_articles = pickle.load(f)


    # https://twitter.com/realDonaldTrump/status/1021007656511852544
    name = 'twitter_tree'

    def parse(self, response):
        driver = webdriver.Chrome(executable_path='./chromedriver')
        driver.get(response.url)
        myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        time.sleep(5)
        self.get_ids_all(driver)

    def get_ids_all(self, driver):
        page = driver.find_element_by_tag_name('body')
        prev_links = None
        while True:
            while True:
            # for i in range(30):
                timeline = driver.find_element_by_css_selector('div[aria-label="Timeline: Conversation"]')
                articles = timeline.find_elements_by_css_selector('article[role="article"][data-focusable="true"]')
                new_links = []
                for a in articles:
                    try:
                        links = self.get_status_link(a)
                        for l in links:
                            new_links.append(l)
                    except Exception as e:
                        continue
                    finally:
                        time.sleep(0.4)

                if self.same_articles(prev_links, new_links):
                    break
                else:
                    for l in new_links:
                        self.all_articles.append(l)
                    prev_links = new_links
                    self.all_articles = list(set(self.all_articles))
                    print('article num: {}'.format(len(self.all_articles)))
                    page.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.4)
                    page.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.4)

            more = driver.find_elements_by_css_selector('div[role="button"][data-focusable="true"]')
            more = [x for x in more if 'Show more replies' in x.text]
            if len(more) > 0:
                flag = False
                while True:
                    try:
                        if flag:
                            break
                        more[0].click()
                        flag = True
                        time.sleep(2)
                    except:
                        page.send_keys(Keys.PAGE_UP)
                        pass
            else:
                with open('{}.pkl'.format(self.tweet_id), 'wb') as f:
                    pickle.dump(self.all_articles, f)
                break


    def get_ids_one_page(self, driver):
        try:
            prev_articles = None
            first_flag = False
            while True:
                page = driver.find_element_by_tag_name('body')
                timeline = driver.find_element_by_css_selector('div[aria-label="Timeline: Conversation"]')
                articles = timeline.find_elements_by_css_selector('article[role="article"][data-focusable="true"]')
                if self.same_articles(prev_articles, articles):
                    break
                else:
                    prev_articles = [x.text for x in articles]

                for a in articles:
                    try:
                        print(a.text)
                    except:
                        continue
                    if 'ApionisHesychia' in a.text:
                        pdb.set_trace()
                    try:
                        reply = a.find_element_by_css_selector('div[data-testid="reply"]').text
                    except:
                        continue

                    if self.get_meta_data(a, reply) in self.all_articles:
                        continue
                    try:
                        text = a.find_element_by_css_selector('div[lang="en"]')
                    except:
                        continue
                    if reply == '' and not first_flag:
                        first_flag = True
                    else:
                        self.all_articles.append(self.get_meta_data(a, reply))

                    time.sleep(0.4)
                        
                page.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.4)

        except Exception as e:
            print(e)
            if not os.path.exists('{}.pkl'.format(self.tweet_id)):
                with open('{}.pkl'.format(self.tweet_id), 'wb') as f:
                    pickle.dump(self.all_articles, f)
            else:
                with open('{}.pkl'.format(self.tweet_id), 'rb') as f:
                    tmp = pickle.load(f)
                    if len(tmp) < len(self.all_articles):
                        with open('{}.pkl'.format(self.tweet_id), 'wb') as f:
                            pickle.dump(self.all_articles, f)

    def get_all_ids(self, driver):
        try:
            self.all_urls.append(driver.current_url)
            while True:
                page = driver.find_element_by_tag_name('body')
                prev_articles = None
                while True:
                    timeline = driver.find_element_by_css_selector('div[aria-label="Timeline: Conversation"]')
                    articles = timeline.find_elements_by_css_selector('article[role="article"][data-focusable="true"]')
                    if self.same_articles(prev_articles, articles):
                        break
                    else:
                        prev_articles = [x.text for x in articles]

                    first_flag = False
                    for a in articles:
                        print(a.text)
                        if 'ApionisHesychia' in a.text:
                            pdb.set_trace()
                        try:
                            reply = a.find_element_by_css_selector('div[data-testid="reply"]').text
                        except:
                            continue

                        if self.get_meta_data(a, reply) in self.all_articles:
                            continue
                        try:
                            text = a.find_element_by_css_selector('div[lang="en"]')
                        except:
                            continue
                        if reply.isdigit() and first_flag:
                            self.all_articles.append(self.get_meta_data(a, reply))

                            action = ActionChains(driver)
                            action.reset_actions()
                            action.move_to_element(text).perform()
                            action.key_down(Keys.COMMAND).click(text).key_up(Keys.COMMAND).perform()
                            driver.switch_to_window(driver.window_handles[-1])
                            # text.click()
                            time.sleep(2)
                            self.get_all_ids(driver) 
                        elif reply == '' and not first_flag:
                            first_flag = True
                        elif reply == '':
                            self.all_articles.append(self.get_meta_data(a, reply))

                        time.sleep(0.4)
                            
                    page.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.4)

                page.send_keys(Keys.PAGE_UP)
                more = driver.find_elements_by_css_selector('div[role="button"][data-focusable="true"]')
                more = [x for x in more if 'Show more replies' in x.text]
                if len(more) > 0:
                    more[0].click()
                    time.sleep(2)
                else:
                    # driver.execute_script("window.history.go(-1)")
                    # driver.navigate().back()
                    driver.close()
                    driver.switch_to_window(driver.window_handles[-1])
                    time.sleep(1)
                    break
        except Exception as e:
            print(e)
            if not os.path.exists('{}.pkl'.format(self.tweet_id)):
                with open('{}.pkl'.format(self.tweet_id), 'wb') as f:
                    pickle.dump(self.all_articles, f)
            else:
                with open('{}.pkl'.format(self.tweet_id), 'rb') as f:
                    tmp = pickle.load(f)
                    if len(tmp) < len(self.all_articles):
                        with open('{}.pkl'.format(self.tweet_id), 'wb') as f:
                            pickle.dump(self.all_articles, f)

    def same_articles(self, prev_articles, articles):
        if prev_articles is None:
            return False

        if len(articles) == 0:
            return True

        else:
            if len(prev_articles) != len(articles):
                return False
            else:
                return prev_articles[-1] == articles[-1]

    def is_all_append(self, articles):
        texts = [x.text for x in articles]

        return all([True if text in self.all_articles else False for text in texts])

    def get_meta_data(self, article, reply=None):
        retweet = article.find_element_by_css_selector('div[data-testid="reply"]').text
        like = article.find_element_by_css_selector('div[data-testid="like"]').text
        res = [article.text]
        if reply is None:
            reply = article.find_element_by_css_selector('div[data-testid="reply"]').text
        if reply != '':
            res.append('reply')
        if retweet != '':
            res.append('retweet')
        if like != '':
            res.append('like')

        link = article.find_elements_by_tag_name('a')
        if len(link) > 0:
            res.append(link[0].get_attribute('href'))

        return ' '.join(res)

    def get_status_link(self, article, reply='0'):
        link = article.find_elements_by_tag_name('a')
        res = []
        for l in link:
            href = l.get_attribute('href')
            if href and '/status/' in href and '/photo/' not in href:
                if self.tweet_id in href:
                    self.first_tweet = True
                    return []
                if not self.first_tweet:
                    self.bad_articles.append(href)
                    return [] 
                if href in self.bad_articles:
                    return []

                res.append(href)

        try:
            reply = article.find_element_by_css_selector('div[data-testid="reply"]').text
            if reply == '':
                reply = '0'
        except: 
            pass

        for i in range(len(res)):
            res[i] = '{}-{}'.format(res[i], reply)

        return res
