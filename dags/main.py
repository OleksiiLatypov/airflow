from bs4 import BeautifulSoup
import requests

headers = {
    "Referer": 'https://www.amazon.com/',
    "Sec-Ch-Ua": "Not_A Brand",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}


base_url = f"https://www.amazon.com/s?k=data+engineering+books"
check = requests.get(base_url, headers=headers)
print(check)

books = []
seen_title = set()

for i in range(1):
    url = f'{base_url}&page={i}'
    response = requests.get(url, headers=headers)
    print(response)
    #print(requests.get(page, headers=headers))
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        authors = soup.find_all('a', {'class': 'a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style'})
        print(authors)

