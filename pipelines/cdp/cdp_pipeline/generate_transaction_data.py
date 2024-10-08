from google.cloud import storage
from google.cloud import pubsub_v1
import csv
import json
import pandas as pd
import asyncio
import time

async def publish_coupons_to_pubsub():
    bucket_name = '<bucket_name>'
    project_id = '<project_id>'
    
    transactions_id = ['<List of sample transaction IDs to test the pipeline on.>'] # For example - ['27601281299','27757099033','28235291311','27021203242','27101290145','27853175697']
    transactions_topic_name = "transactions"
    transactions_data = '<path to transactions data in gcs bucket>' # reference example - 'dataflow-solution-guide-cdp/input_data/transaction_data.csv'
    coupons_topic_name = "coupon_redemption"
    coupons_data = '<path to coupon redemption data in gcs bucket>' # reference example - 'dataflow-solution-guide-cdp/input_data/coupon_redempt.csv'
                                                                     
    transactions_df = pd.read_csv(f"gs://{bucket_name}/{transactions_data}",dtype=str)
    coupons_df = pd.read_csv(f"gs://{bucket_name}/{coupons_data}",dtype=str)
    publisher = pubsub_v1.PublisherClient() 
  
    transactions_topic_path = publisher.topic_path(project_id, transactions_topic_name)
    coupons_topic_path = publisher.topic_path(project_id, coupons_topic_name)
    filtered_trans_df = transactions_df[transactions_df['transaction_id'].isin(transactions_id)]
    filtered_coupons_df = coupons_df[coupons_df['transaction_id'].isin(transactions_id)]
    await asyncio.gather(publish_coupons(filtered_coupons_df,publisher,coupons_topic_path), publish_transactions(filtered_trans_df,publisher,transactions_topic_path))
        
async def publish_coupons(filtered_coupons_df,publisher,coupons_topic_path):
    for _, row in filtered_coupons_df.iterrows():
            coupon_message = json.dumps(row.to_dict()).encode('utf-8')
            print(coupon_message)
            future = publisher.publish(coupons_topic_path, coupon_message)
            print(f"Published  coupon message ID: {future.result()}")
            await asyncio.sleep(3)

async def publish_transactions(filtered_trans_df,publisher,transactions_topic_path):
    for  _, row in filtered_trans_df.iterrows():
            transaction_message = json.dumps(row.to_dict()).encode('utf-8')
            print(transaction_message)
            future = publisher.publish(transactions_topic_path, transaction_message)
            print(f"Published transaction message ID: {future.result()}")
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(publish_coupons_to_pubsub())