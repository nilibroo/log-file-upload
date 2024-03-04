import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as lambda_
from aws_cdk import aws_apigateway as apigw


from constructs import Construct

class LogFileUploadStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Buckets
        uncompressed_bucket = s3.Bucket(self, "UncompressedBucket")
        compressed_bucket = s3.Bucket(self, "CompressedBucket")

        # Lambda Function to compress log file content
        compress_lambda = lambda_.Function(
            self, "CompressLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="compress.handler",
            code=lambda_.Code.from_asset("log_file_upload/lambda"),
            
            environment={
                'UNCOMPRESSED_BUCKET': uncompressed_bucket.bucket_name,
                'COMPRESSED_BUCKET': compressed_bucket.bucket_name
            }
        )

        # Lambda Function to process log file content
        process_lambda = lambda_.Function(
            self, "ProcessLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="process.handler",
            code=lambda_.Code.from_asset("log_file_upload/lambda"),
            
            environment={
                'UNCOMPRESSED_BUCKET': uncompressed_bucket.bucket_name,
                'COMPRESSED_BUCKET': compressed_bucket.bucket_name,
                'COMPRESS_LAMBDA_ARN': compress_lambda.function_arn,
            }
        )

        # Grant Lambda permissions to write to S3 buckets
        uncompressed_bucket.grant_write(process_lambda)
        # uncompressed_bucket.grant_read(compress_lambda)
        compressed_bucket.grant_write(compress_lambda)

        # Grant Lambda permissions to invoke another Lambda function
        compress_lambda.grant_invoke(process_lambda)

        # API Gateway
        api = apigw.RestApi(self, 'LogUploadApi')

        # Define API Gateway method to handle POST requests
        log_resource = api.root.add_resource('log')
        log_resource.add_method('POST', apigw.LambdaIntegration(process_lambda))