import scrapy
import json
from datetime import datetime as dt
from ..items import InstagramTagItem, InstagramPostItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    start_urls = ['https://www.instagram.com/']
    query_hash = {
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32'
    }
    tag_list = ['python']

    def __init__(self, login, password, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            # if successfully authorized
            if response.json().get('authenticated'):
                for tag in self.tag_list:
                    yield response.follow(f'/explore/tags/{tag}', callback=self.tag_parse)

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])

    def tag_parse(self, response):
        data = self.js_data_extract(response)
        data_dict = data['entry_data']['TagPage'][0]['data']

        hashtag_instagram_id = data_dict['id']
        hashtag_name = data_dict['name']
        hashtag_profile_pic_url = data_dict['profile_pic_url']
        item = InstagramTagItem(
            instagram_id=hashtag_instagram_id,
            name=hashtag_name,
            picture_url=hashtag_profile_pic_url,
        )
        yield item

        yield from self.instagram_posts_page_parse(response)

    def instagram_posts_page_parse(self, response):
        try:
            data = self.js_data_extract(response)
            data_dict = data['entry_data']['TagPage'][0]['data']
        except AttributeError as e:
            data = json.loads(response.text)
            data_dict = data['data']

        # hashtag_name = data_dict['name']
        edge_hashtag_to_media = data_dict['recent']
        sections = edge_hashtag_to_media['sections']
        for section in sections:
            for el in section['layout_content']['medias']:
                node = el['media']
                if node.get('image_versions2'):
                    display_url = node['image_versions2']['candidates'][0]['url']
                    item_post = InstagramPostItem(
                        data=json.dumps(data),
                        picture_url=display_url,
                        date_parse=dt.now(),
                    )
                else:
                    item_post = InstagramPostItem(
                        data=node,
                        date_parse=dt.now(),
                    )
                yield item_post

        # page_info = edge_hashtag_to_media['page_info']
        # if page_info['has_next_page']:
        #     let_end_cursor = page_info['end_cursor']
        #     url_begin = 'https://www.instagram.com/graphql/query/?'
        #     param_query_hash = f'query_hash={self.query_hash["tag_paginate"]}'
        #     let_tag_name = f'"tag_name"%3A"{hashtag_name}"'
        #     let_first = f'"first"%3A100'
        #     let_after = f'"after"%3A"{let_end_cursor}"'
        #     url = f'{url_begin}{param_query_hash}&variables=%7B{let_tag_name},{let_first},{let_after}%7D'
        #     yield response.follow(url, callback=self.instagram_posts_page_parse)
