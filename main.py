import asyncio
import csv
import os
import random
import re

import aiohttp

from math import floor
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm

MAIN_PAGE_URL = 'https://www.eu-startups.com/directory/'

BASE_DIR = os.getcwd()

RESULT_FILE_PATH = os.path.join(BASE_DIR, 'result.csv')

headers = [
    {
        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
        'Accept-Language': 'en-US',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html',
    },
    {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html',
    },
    {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html',
    },
    {
        'User-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1a',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html',
    },
    {
        'User-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1a',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html',
    }
]


async def get_page_data(url):
    try:
        async with aiohttp.ClientSession(headers=headers[random.randrange(0, len(headers) - 1)]) as session:
            async with session.get(url) as response:
                await asyncio.sleep(2)
                return await response.text(encoding='utf-8')
    except:
        raise Exception('Lost connection, website denied the connection')


def get_total_of_categories(main_page: BeautifulSoup) -> int:
    try:
        categories = [int(re.sub('[()]', '', li.parent.contents[-1].strip()))
                      for li in main_page.find_all('a', class_='category-label')]

        return sum(categories)
    except Exception:
        raise Exception('Category not found')


def get_max_page(main_page: BeautifulSoup) -> int:
    total = get_total_of_categories(main_page)
    return floor(total / 11)


async def scrap_company_detail(url: str):
    html = await get_page_data(url)
    bs = BeautifulSoup(html, 'lxml')
    try:
        title = bs.find('h1', class_='td-page-title').text
    except Exception:
        raise Exception(f'Title not found: {url}')

    try:
        website = [block.find_next('div').text for block in bs.find_all('span', class_='field-label')
                   if block.text == 'Website']
    except Exception:
        raise Exception(f'Website not found {url}')

    try:
        with open(RESULT_FILE_PATH, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([title.strip(), ' '.join(website)])
    except:
        raise Exception('Failed to open results.csv file')

    main_progress_bar.update()


async def scrap_company(page_num: int):
    url = urljoin(MAIN_PAGE_URL, f'page/{page_num}/')
    html = await get_page_data(url)
    bs = BeautifulSoup(html, 'lxml')
    company_detail_urls = [title_block.find_next('a').get('href')
                           for title_block in bs.find_all('div', class_='listing-title')]

    await asyncio.gather(*[scrap_company_detail(com_url) for com_url in company_detail_urls])


async def main():
    tasks = []
    html = await get_page_data(MAIN_PAGE_URL)
    bs = BeautifulSoup(html, 'lxml')
    global main_progress_bar
    main_progress_bar = tqdm(total=get_total_of_categories(bs), colour='#50C878')
    for page in range(1, get_max_page(bs) + 1):
        tasks.append(asyncio.create_task(scrap_company(page)))
        await asyncio.sleep(0.1)
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    with open(RESULT_FILE_PATH, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['Company name', 'Website'])
        f.close()
    asyncio.run(main())
    input()
