import datetime
import json
import traceback
import boto3
import os

s3 = None

# Insanciate s3 client globally and lazily
def get_s3_client():
    global s3
    if not s3:
        s3 = boto3.client('s3')
    return s3

def handler(event, context):
    try:

        # Retrieve bucket names from environment variables
        uncompressed_bucket_name = os.environ['UNCOMPRESSED_BUCKET'] 

        # Retrieve ompress lambda from environment variables
        compress_lambda_arn = os.environ['COMPRESS_LAMBDA_ARN']

        # Extract log file content from the event
        log_content = event['body']

        # Store log file in uncompressed S3 bucket
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"log_file_{timestamp}.txt"
        get_s3_client().put_object(Bucket=uncompressed_bucket_name, Key=file_name, Body=log_content)

        # Trigger another Lambda function to handle compression
        payload = {
            'timestamp': timestamp,
            'content': log_content
            }  
        
        lambda_client = boto3.client('lambda')
        response = lambda_client.invoke(
            FunctionName=compress_lambda_arn,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload),
        )

        # Check if the invocation was successful
        response_payload = json.loads(response['Payload'].read())
        if response_payload['statusCode'] != 200:
            # Handle the error returned from the compress Lambda
            raise Exception(f"Error from compress Lambda: {response_payload['body']}")

        return {
            'statusCode': 200,
            'body': json.dumps('Log file uploaded successfully')
        }
    
    except Exception as e:
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }