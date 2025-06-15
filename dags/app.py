from datetime import datetime, timedelta
from airflow import DAG
import requests
import pandas as pd
from bs4 import BeautifulSoup
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

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
        url = f'{base_url}&page={page}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        containers = soup.find_all("div", class_="a-section a-spacing-small puis-padding-left-small puis-padding-right-small")

        for container in containers:
            title_tag = container.find("h2")
            title = title_tag.text.strip() if title_tag else None

            author_tag = container.find("a", class_="a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style")
            author = author_tag.text.strip() if author_tag else None

            rating_tag = container.find("span", class_="a-icon-alt")
            rating = rating_tag.text.strip() if rating_tag else None

            rating_count_tag = container.find("span", class_="a-size-base s-underline-text")
            rating_count = rating_count_tag.text.strip() if rating_count_tag else None

            price_tag = container.find("span", string=lambda text: text and "$" in text)
            price = price_tag.text.strip() if price_tag else None

            if title and title not in unique_books:
                unique_books.add(title)
                books.append({
                    "title": title,
                    "author": author,
                    "rating": rating,
                    "rating_count": rating_count,
                    "price": price
                })

    ti.xcom_push(key='book_data', value=books)


def insert_data_to_postgres(ti):
    book_data = ti.xcom_pull(key='book_data', task_ids='get_book_data')
    if not book_data:
        raise ValueError("No book data found")

    hook = PostgresHook(postgres_conn_id='books_connection')
    conn = hook.get_conn()
    cursor = conn.cursor()

    for book in book_data:
        cursor.execute("""
            INSERT INTO book (title, author, rating, rating_count, price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            book['title'], book['author'], book['rating'], book['rating_count'], book['price']
        ))

    conn.commit()
    cursor.close()
    conn.close()


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='fetch_and_store_amazon_books',
    default_args=default_args,
    description='A simple DAG to fetch book data from Amazon and store it in Postgres',
    schedule='@daily',
    catchup=False,
)

create_table_task = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='books_connection',
    sql="""
        CREATE TABLE IF NOT EXISTS book (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            rating TEXT,
            rating_count TEXT,
            price TEXT
        )
    """,
    dag=dag
)

get_book_data_task = PythonOperator(
    task_id='get_book_data',
    python_callable=get_amazon_books,
    op_args=[5],  # pages to scrape
    dag=dag
)

insert_book_data_task = PythonOperator(
    task_id='insert_book_data',
    python_callable=insert_data_to_postgres,
    dag=dag
)

create_table_task >> get_book_data_task >> insert_book_data_task
