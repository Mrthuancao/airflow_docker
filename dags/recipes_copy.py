import datetime as dt
import json
import os
import uuid
from time import sleep

import requests
from airflow import DAG
from airflow.hooks.mysql_hook import MySqlHook
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from bs4 import BeautifulSoup
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

# def scrape_sports():
    # website = "https://www.thesun.co.uk/sport/football/"
    # page = requests.get(website)
    # soup = BeautifulSoup(page.content, "html.parser")
    # elements = soup.find_all("div", class_="teaser__copy-container")

    # sports_data = []
    # for element in elements:
    #     title_element = element.find("h3", class_="teaser__headline")
    #     subtitle_element = element.find("p", class_="teaser__subdeck")
    #     link_element = element.find("a", class_="text-anchor-wrap")

    #     if title_element is not None and subtitle_element is not None and link_element is not None:
    #         title = title_element.text.strip()
    #         subtitle = subtitle_element.text.strip()
    #         link = link_element['href']
    #         sports_data.append((title, subtitle, link))

    # print(sports_data)
    # return sports_data

    # Scrape tuko news
def scrape_politics():
    website = "https://www.tuko.co.ke/politics/"
    page = requests.get(website)
    soup = BeautifulSoup(page.content, "html.parser")
    elements = soup.find_all("article", class_="c-article-card-no-border")

    politics_data = []
    for element in elements:
        title = element.find("a", class_="c-article-card-no-border__headline").text.strip()
        link = element.find("a")["href"]
        date = element.find("time")["datetime"]  
        politics_data.append((title, link, date))
    
    # create_table("Politics", ["Title VARCHAR(255)","Link VARCHAR(255)","Date DATE"])
    # populate_table("Politics", politics_data)
    print(politics_data)
    return politics_data




def store_data(**kwargs):
    ti = kwargs['ti']

    parsed_records = ti.xcom_pull(task_ids='scrape_politics', dag_id='scrape_news', include_prior_dates=True)
    hook = PostgresHook(postgres_conn_id='postgres_localhost', schema='postgres')
    conn = hook.get_conn()
    cursor = conn.cursor()
    print(parsed_records)

    for r in parsed_records:
        translate_table = str.maketrans({"'": r"''"})
        link = r[1].translate(translate_table)
        title = r[0].translate(translate_table)
        print(title, link)
        sql = f'''
        INSERT INTO postgres.public.recipes(url,data) VALUES ('{title}','{link}')
        '''
        # sql = 'INSERT INTO postgres.public.recipes(url,data) VALUES ("data","data")'
        cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()
    return True


default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2018, 10, 3, 15, 58, 00),
    'concurrency': 1,
    'retries': 0
}

with DAG('scrape_new_from_other_dags',
         catchup=False,
         default_args=default_args,
         schedule_interval='*/2 * * * *',
         # schedule_interval=None,
         ) as dag:
    # opr_parse_recipes = PythonOperator(task_id='scrape_politics',
    #                                    python_callable=scrape_politics, provide_context=True)

    # opr_download_image = PythonOperator(task_id='download_image',
    #                                     python_callable=download_image, provide_context=True)

    opr_store_data = PythonOperator(task_id='store_data',
                                    python_callable=store_data, provide_context=True)

    # task2 = PostgresOperator(
    #     task_id='insert_into_table',
    #     postgres_conn_id='postgres_localhost',
    #     sql="""
    #         insert into recipes (url, data) values ('123', '132')
    #         """
    # )


opr_store_data 