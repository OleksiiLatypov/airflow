# from bs4 import BeautifulSoup
# import requests
# from pprint import pprint
#
# headers = {
#     "Referer": 'https://www.amazon.com/',
#     "Sec-Ch-Ua": "Not_A Brand",
#     "Sec-Ch-Ua-Mobile": "?0",
#     "Sec-Ch-Ua-Platform": "macOS",
#     'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
# }
#
# base_url = f"https://www.amazon.com/s?k=data+engineering+books"
# check = requests.get(base_url, headers=headers)
# print(check)
#
# books = []
# seen_title = set()
# titles = []
# authors = []
#
# for i in range(1):
#     url = f'{base_url}&page={i}'
#     response = requests.get(url, headers=headers)
#     print(response)
#     # print(requests.get(page, headers=headers))
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         # result = soup.find_all('div', {'data-component-type': 's-search-result'})
#         result = soup.find_all('div', class_="a-section a-spacing-small puis-padding-left-small puis-padding-right-small")
#         print("Found results:", len(result))
#         print(len(result))
#
#         # for item in result:
#         #     title = item.find('h2')
#         #     titles.append(title.text.strip())
#         #     author = item.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style')
#         #     authors.append(author.text.strip())
# print(len(titles))
# print(len(authors))

from bs4 import BeautifulSoup
import requests
from pprint import pprint

headers = {
    "Referer": "https://www.amazon.com/",
    "Sec-Ch-Ua": "Not_A Brand",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

base_url = "https://www.amazon.com/s?k=data+engineering+books"

response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

books = []

# Select all book containers
containers = soup.find_all("div", class_="a-section a-spacing-small puis-padding-left-small puis-padding-right-small")
print(f"Found {len(containers)} books")

for container in containers:
    # Title
    title_tag = container.find("h2")
    title = title_tag.text.strip() if title_tag else None

    # Author
    author_tag = container.find("a", class_="a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style")
    author = author_tag.text.strip() if author_tag else None

    # Rating
    rating_tag = container.find("span", class_="a-icon-alt")
    rating = rating_tag.text.strip() if rating_tag else None

    # Number of ratings
    rating_count_tag = container.find("span", class_="a-size-base s-underline-text")
    rating_count = rating_count_tag.text.strip() if rating_count_tag else None

    # Price (look for span with dollar sign)
    price_tag = container.find("span", string=lambda text: text and "$" in text)
    price = price_tag.text.strip() if price_tag else None

    # Store the extracted info
    if title:
        books.append({
            "title": title,
            "author": author,
            "rating": rating,
            "rating_count": rating_count,
            "price": price
        })

pprint(books)

