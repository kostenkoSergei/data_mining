from urllib.parse import unquote
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader
from scrapy import Selector
from .items import HHVacancyItem, HHCompaniesItem


def symbols_delete(itm):
    result = itm.replace('\xa0', '')
    return result


def list_to_string_with_space(itm):
    result = ' '.join(itm)
    return symbols_delete(result)


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = list_to_string_with_space
    salary_out = TakeFirst()
    description_in = list_to_string_with_space
    description_out = TakeFirst()
    skills_out = MapCompose(symbols_delete)


class HHCompaniesLoader(ItemLoader):
    default_item_class = HHCompaniesItem
    url_out = TakeFirst()
    title_in = list_to_string_with_space
    title_out = TakeFirst()
    company_url_out = TakeFirst()
    field_of_work_out = MapCompose(symbols_delete)
    description_in = list_to_string_with_space
    description_out = TakeFirst()
