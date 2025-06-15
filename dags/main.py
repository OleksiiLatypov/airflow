import json
import pandas as pd
from bs4 import BeautifulSoup
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
from pprint import pprint
from datetime import datetime, timedelta
from airflow import DAG

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_and_store_amazon_books',
    default_args=default_args,
    description='A simple DAG to fetch book data from Amazon and store it in Postgres',
    schedule=timedelta(days=1),
)

headers = {
    "Referer": "https://www.amazon.com/",
    "Sec-Ch-Ua": "Not_A Brand",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

base_url = "https://www.amazon.com/s?k=data+engineering+books"


def get_amazon_books(pages: int, ti):
    books = []
    unique_books = set()

    for page in range(1, pages + 1):
        print(f'Page num: {page}')
        url = f'{base_url}&page={page}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Select all book containers
        containers = soup.find_all("div",
                                   class_="a-section a-spacing-small puis-padding-left-small puis-padding-right-small")
        # print(f"Found {len(containers)} books")

        for container in containers:

            # Title
            title_tag = container.find("h2")
            title = title_tag.text.strip() if title_tag else None

            # Author
            author_tag = container.find("a",
                                        class_="a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style")
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
            if title and title not in unique_books:
                unique_books.add(title)
                books.append({
                    "title": title,
                    "author": author,
                    "rating": rating,
                    "rating_count": rating_count,
                    "price": price
                })
    print(len(books))
    print(len(unique_books))

    data = pd.DataFrame(books)

    print(data.head())
    print(f'Duplicated data: {data.duplicated().sum()}')
    with open('books.json', 'w') as f:
        json.dump(books, f, indent=8)

    # Push the DataFrame to XCom
    ti.xcom_push(key='book_data', value=data.to_dict('records'))


def insert_data_to_postgres(ti):
    book_data = ti.xcom_pull(key='book_data', task_ids='fetch_book_data')
    if not book_data:
        raise ValueError("No book data found")



create_table_task = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='books_connection',
    sql_script="""CREATE TABLE IF NOT EXISTS book
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    rating TEXT,
                    rating_count TEXT,
                    price TEXT""",
    dag=dag
)




if __name__ == '__main__':
    print(get_amazon_books(10, None))
