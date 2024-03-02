import gzip
import json
import boto3
import os

s3 = boto3.client('s3')


def handler(event, context):
    try:
        # Retrieve bucket names from environment variables
        uncompressed_bucket_name = os.environ['UNCOMPRESSED_BUCKET']
        compressed_bucket_name = os.environ['COMPRESSED_BUCKET']

        # Get the uploaded log file from uncompressed bucket
        obj = s3.get_object(Bucket=uncompressed_bucket_name, Key='log_file.txt')
        log_content = obj['Body'].read()

        # Compress the log file content
        compressed_content = gzip.compress(log_content)

        # Store compressed log file in compressed S3 bucket
        s3.put_object(Bucket="CompressedBucket", Key='log_file.txt.gz', Body=compressed_content)

        return {
            'statusCode': 200,
            'body': 'Log file compressed and stored successfully'
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(e)
        }