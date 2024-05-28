import json
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(filename='app.log', level=logging.DEBUG)


def get_category(url):
    """Получает url категории товаров, выполняет GET-запрос к указанному URL и возвращает JSON-ответ от сервера."""
    response = requests.get(url)
    if response.status_code != 200:
        logging.error("Не удалось получить данные главной страницы категории.")
        raise ValueError(f"Ошибка при попытке получить данные по ссылке - {url}!")

    return response.json()


def get_products(response):
    """Получает JSON c товарами, собирает список словарей с нужными данными и возвращет его."""
    products_response = response.get('data', {}).get('products')
    if not products_response:
        logging.error("Не удалось получить список товаров в категории.")
        raise ValueError("Список товаров пуст!")

    products = []
    for product in products_response:
        products.append({
            'title': product.get('name'),
            'price': f"{product.get('sizes')[0].get('price', {}).get('basic', 0) // 100} руб.",
            'link': f"https://www.wildberries.ru/catalog/{product.get('id')}/detail.aspx",
        })

    return products


def main():
    # список ссылок на разные категории товаров
    urls = [
        'https://catalog.wb.ru/catalog/sport14/v2/catalog?appType=1&curr=rub&dest=-1292749&sort=popular&spp=30&subject=2151&uclusters=3',
        'https://catalog.wb.ru/catalog/jewellery1/v2/catalog?appType=1&curr=rub&dest=-1292749&sort=popular&spp=30&subject=54&uclusters=3',
        'https://catalog.wb.ru/catalog/sport32/v2/catalog?appType=1&cat=10405&curr=rub&dest=-1292749&sort=popular&spp=30&uclusters=3',
        'https://catalog.wb.ru/catalog/interior3/v2/catalog?appType=1&curr=rub&dest=-1292749&sort=popular&spp=30&subject=198&uclusters=3',
        'https://catalog.wb.ru/catalog/books3/v2/catalog?appType=1&cat=9157&curr=rub&dest=-1292749&sort=popular&spp=30&uclusters=3',
    ]

    # запускаем параллельную загрузку данных
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(get_category, urls))

    # сохраняем результат в JSON отдельно по каждой категории
    suffix = 0
    for result in results:
        products = get_products(result)
        with open(f'integraaal_wb_{suffix}.json', 'w') as file:
            json.dump(products, file, ensure_ascii=False, indent=4)
        suffix += 1


if __name__ == '__main__':
    main()
