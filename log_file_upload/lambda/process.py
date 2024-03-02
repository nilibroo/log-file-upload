import json
import boto3

s3 = boto3.client('s3')


def handler(event, context):
    # Retrieve bucket names from environment variables
    uncompressed_bucket_name = event['UNCOMPRESSED_BUCKET']
    compressed_bucket_name = event['COMPRESSED_BUCKET']

    # Extract log file content from the event
    log_content = event['body']

    # Store log file in uncompressed S3 bucket
    s3.put_object(Bucket=uncompressed_bucket_name, Key='log_file.txt', Body=log_content)

    # Compress log file and store in compressed S3 bucket
    # Trigger another Lambda function to handle compression
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName=context.invoked_function_arn,
        InvocationType='Event',
        Payload=json.dumps(event)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Log file uploaded successfully')
    }