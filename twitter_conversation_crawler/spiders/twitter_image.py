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


class TwitterImage(scrapy.Spider):
    def __init__(self, tweet_id=None):
        self.start_urls = [
            "https://twitter.com/Nigel21915926/status/%s" % tweet_id]
        self.tweet_id = tweet_id
        self.all_articles = []
        self.first_tweet = False
        self.bad_articles = []

    name = 'twitter_image'

    def parse(self, response):
        driver = webdriver.Chrome(
            executable_path='./chromedriver')
        driver.get(response.url)
        myElem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body')))

        time.sleep(5)

        self.get_single_tweet(driver)

    def get_single_tweet(self, driver):
        page = driver.find_element_by_tag_name('body')
        prev_links = None

        timeline = driver.find_element_by_css_selector(
            'div[aria-label="Timeline: Conversation"]')
        articles = timeline.find_elements_by_css_selector(
            'article[role="article"][data-focusable="true"]')
        # crawl only the main post
        article = None
        for a in articles:
            reply = a.find_element_by_css_selector('div[data-testid="reply"]').text
            if reply == '':
                article = a
                break

        imgs = self.get_img_link(article)
        for i, img in enumerate(imgs):
            t = img.format
            img.save('./{}-{}.{}'.format(self.tweet_id, i, t))

    def get_img_link(self, article):
        link = article.find_elements_by_tag_name('img')
        imgs = []
        for l in link:
            imgalt = l.get_attribute('alt')
            if imgalt != 'Image':
                continue
            imgsrc = l.get_attribute('src')
            img = Image.open(urllib.request.urlopen(imgsrc))
            imgs.append(img)

        return imgs
