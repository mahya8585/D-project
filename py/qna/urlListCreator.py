import requests
from bs4 import BeautifulSoup
from time import sleep


def get_paging_info(url):
    """
    nextボタンに紐づくURLを取得する
    :param: url 取得ページURL
    :return: beautifulsoup nextボタンのaタグ
    """
    category_top = requests.get(url, headers=headers)

    # DoS扱いにならないためにスリープ
    sleep(3)

    top_soup = BeautifulSoup(category_top.text, 'html.parser')
    paging = top_soup.find('div', class_='paging')
    if paging is None:
        return None

    next_button = paging.find('li', class_='next')

    return next_button.find('a')


categories = [
    '270',
    '5',
    '12',
    '38',
    '124',
    '130',
    '159',
    '193',
    '219',
    '302',
    '403',
    '418',
    '948'
]

domain = 'https://faq.tokyodisneyresort.jp/tdr/'
page_prefix = 'faq_list.html?page=&category='
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}

urls = []

for category in categories:
    print(category + 'のURL収集中...')
    url = domain + page_prefix + category
    urls.append(url)

    next_page = get_paging_info(url)

    if next_page is None:
        continue
    else:
        next = True
        next_url = domain + next_page.get('href')
        urls.append(next_url)

        while (next):
            category_next = get_paging_info(next_url)

            if category_next is None:
                next = False
            else:
                next_url = domain + category_next.get('href')
                urls.append(next_url)

f = open('urls.txt', 'w')
for url in urls:
    f.write(url + '\n')
f.close()
