import json
import time
from pathlib import Path
import requests

"""
https://5ka.ru/special_offers/
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в 
Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно 
соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    params = {
        "records_per_page": 20,
    }

    start_url = "https://5ka.ru/api/v2/special_offers/"

    def __init__(self, category_code: int):
        self.category_code = category_code

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(2)

    def run(self):
        return self._parse(self.start_url)

    def _parse(self, url: str):
        while url:
            time.sleep(0.1)
            self.params.update({"categories": self.category_code})
            response = self._get_response(url, headers=self.headers, params=self.params)
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product


class Parse5kaCat:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    def __init__(self, url: str):
        self.cat_url = url

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def _parse(self, url: str):
        categories = []
        time.sleep(0.1)
        response = self._get_response(url, headers=self.headers)
        data = response.json()
        for cat_data in data:
            categories.append((cat_data['parent_group_code'], cat_data['parent_group_name']))
        return categories

    def run(self):
        return self._parse(self.cat_url)


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    def get_products_by_categories():
        cat_url = "https://5ka.ru/api/v2/categories/"
        cat = Parse5kaCat(cat_url)
        categories = cat.run()

        for cat_code, cat_name in categories:
            prod = Parse5ka(int(cat_code))
            data = {
                "name": cat_name,
                "code": int(cat_code),
                "products": list(prod.run())
            }
            file_path = get_save_path("products_by_categories").joinpath(f"{cat_name}.json")
            with open(file_path, 'w', encoding='utf8') as json_file:
                json.dump(data, json_file, ensure_ascii=False)


    get_products_by_categories()
