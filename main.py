import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gbparsers import settings
from dotenv import load_dotenv
from gbparsers.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSpider,
                          login=os.getenv('INST_LOGIN'),
                          enc_password=os.getenv('INST_PSWORD'))
    crawler_process.start()
