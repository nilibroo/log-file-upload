import datetime
import gzip
import json
import traceback
import boto3
import os

s3 = None

def get_s3_client():
    global s3
    if not s3:
        s3 = boto3.client('s3')
    return s3

def handler(event, context):
    try:
        # Retrieve bucket names from environment variables
        compressed_bucket_name = os.environ['COMPRESSED_BUCKET']

        log_content = event['content']
        # print(log_content)

        # Compress the log file content
        compressed_content = gzip.compress(bytes(log_content, 'utf-8'))

        # Store compressed log file in compressed S3 bucket
        timestamp = event['timestamp']
        file_name = f"log_file_{timestamp}.txt.gz"
        get_s3_client().put_object(Bucket=compressed_bucket_name, Key=file_name, Body=compressed_content)

        return {
            'statusCode': 200,
            'body': 'Log file compressed and stored successfully'
        }
    
    except Exception as e:
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }