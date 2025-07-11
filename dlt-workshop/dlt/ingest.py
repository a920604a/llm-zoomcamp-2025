# your_ingest_script.py

import dlt
import requests
import pandas as pd
from datetime import datetime
import os

# 1. 擷取 NYC Taxi API 資料
def fetch_taxi_data():
    print("[*] Fetching taxi data from API...")
    url = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)

    # 時間轉換
    df['Trip_Pickup_DateTime'] = pd.to_datetime(df['Trip_Pickup_DateTime'])

    # 分段分類
    df['tag'] = pd.cut(
        df['Trip_Pickup_DateTime'],
        bins=[
            pd.Timestamp("2009-06-01"),
            pd.Timestamp("2009-06-10"),
            pd.Timestamp("2009-06-20"),
            pd.Timestamp("2009-06-30")
        ],
        labels=["first_10_days", "second_10_days", "last_10_days"],
        right=False
    )

    df = df[df['tag'].notnull()]
    return df


# 2. 建立 dlt 資源
def zoomcamp_data_resource(df):
    yield df


# 3. 執行 DLT pipeline 並寫入 DuckDB
def run_pipeline(df):
    print("[*] Loading data into DuckDB with DLT...")

    @dlt.resource(write_disposition="replace", name="zoomcamp_data")
    def resource():
        yield df

    pipeline = dlt.pipeline(
        pipeline_name="zoomcamp_pipeline",
        destination="duckdb",
        dataset_name="zoomcamp_tagged_data"
    )

    load_info = pipeline.run(resource())
    print(pipeline.last_trace)
    return pipeline.dataset().zoomcamp_data.df()


if __name__ == "__main__":
    df = fetch_taxi_data()
    dataset = run_pipeline(df)
    print("[✓] Ingestion finished. Sample preview:")
    print(dataset.head())
