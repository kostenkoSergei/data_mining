import time
import typing

import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4
from datetime import datetime


class GbBlogParse:
    def __init__(self, start_url, collection):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

    def _get_response(self, url, *args, **kwargs):
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        # print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in tags_list
            if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_post(self, url, soup):
        title_tag = soup.find("h1", attrs={"class": "blogpost-title"})
        article_content = soup.find("article", attrs={"class": "blogpost__article-wrapper"})
        image = article_content.findAll('img')[0].attrs['src']
        date_published = soup.find("div", attrs={"class": "blogpost-date-views"}).find("time").attrs['datetime']
        date_published_datetime_obj = datetime.strptime(date_published.replace('T', ' '), '%Y-%m-%d %H:%M:%S%z')
        article_author = soup.find("div", attrs={"itemprop": "author"})
        author_page_link = \
            article_content.find(lambda tag: tag.name == "a" and 'users' in tag.attrs.get("href", '')).attrs[
                'href']
        commentable_id = soup.find("comments").attrs.get('commentable-id')
        # print(commentable_id)

        data = {
            "url": url,
            "title": title_tag.text,
            "first_img_link": image,
            "published": date_published_datetime_obj,
            "article_author": article_author.text,
            "author_page_link": urljoin("https://gb.ru/", author_page_link),
            "comments": self.get_comments(commentable_id)
        }
        return data

    def get_comments(self, commentable_id):
        comments = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
        }
        comments_url = f"https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={commentable_id}&order=desc"
        response = self._get_response(comments_url, headers=headers)
        data = response.json()
        for el in data:
            user_comment = {el["comment"]["user"]["full_name"]: el["comment"]["body"]}
            comments.append(user_comment)
        return comments

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    collection = MongoClient()["gb_parse_23_04"]["gb_blog_v5"]
    parser = GbBlogParse("https://gb.ru/posts", collection)
    parser.run()
