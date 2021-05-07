from ..loaders import HHCompaniesLoader, HHVacancyLoader
import scrapy


class HhRuSpider(scrapy.Spider):
    name = 'hh.ru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath = {
        'vacancies': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        'pagination': '//div[contains(@class, "bloko-gap")]//a[contains(@class, "HH-Pager-Controls-Next")]/@href',
        'company': '//div[@class="vacancy-company-name-wrapper"]/a/@href',
        'company_vacancies': '//div[@class="employer-sidebar-content"]/div[@class="employer-sidebar-block"]/a/@href',
    }

    # initial page
    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)

        for url in response.xpath(self.xpath['vacancies']):
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response, **kwargs):
        loader = HHVacancyLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="vacancy-title"]//h1/text()')
        loader.add_xpath('salary', '//div[@class="vacancy-title"]//p[@class="vacancy-salary"]//text()')
        loader.add_xpath('description', '//div[@class="vacancy-section"]/div[@class="g-user-content"]//text()')
        loader.add_xpath('skills', '//div[@class="bloko-tag-list"]/div//span/text()')
        yield loader.load_item()

        for url in response.xpath(self.xpath['company']):
            yield response.follow(url, callback=self.company_parse)

    def company_parse(self, response, **kwargs):
        loader = HHCompaniesLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="employer-sidebar-header"]//span//text()')
        loader.add_xpath('company_url', '//div[@class="employer-sidebar-content"]/a/@href')
        loader.add_xpath('areas', '//div[@class="employer-sidebar-block"]/p/text()')
        loader.add_xpath('description', '//div[@class="company-description"]/div[@class="g-user-content"]//text()')
        yield loader.load_item()

        # current company's vacancies
        for url in response.xpath(self.xpath['company_vacancies']):
            yield response.follow(url, callback=self.parse)
