import os
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from process import handler  # Import your handler function


class TestHandler(unittest.TestCase):

    @patch('boto3.client')
    def test_handler_success(self, mock_boto3_client):
        # Mock event data for the log file upload
        event = {
            'body': 'Sample log data',
        }

        # Mock context data
        context = MagicMock()

        # Mock environment variables
        os.environ['UNCOMPRESSED_BUCKET'] = 'uncompressed-bucket'
        os.environ['COMPRESS_LAMBDA_ARN'] = 'arn:aws:lambda:us-east-1:123456789012:function:compress-lambda-function'

        # Mock S3 client
        s3_mock = MagicMock()
        s3_mock.put_object.return_value = {}

        # Mock Lambda client
        lambda_mock = MagicMock()
        lambda_mock.invoke.return_value = {'Payload': MagicMock(read=lambda: '{"statusCode": 200}')}

        mock_boto3_client.side_effect = [s3_mock, lambda_mock]

        # Invoke the handler function
        response = handler(event, context)

        # Check if the response is successful
        self.assertEqual(response['statusCode'], 200)

        # Check if the response body contains the expected message
        self.assertEqual(response['body'], '"Log file uploaded successfully"')

        # Check if the object was stored in the S3 bucket
        s3_mock.put_object.assert_called_once_with(Bucket='uncompressed-bucket', Key=mock.ANY, Body='Sample log data')

        # Check if the compress Lambda function was invoked
        lambda_mock.invoke.assert_called_once_with(
            FunctionName='arn:aws:lambda:us-east-1:123456789012:function:compress-lambda-function',
            InvocationType='RequestResponse',
            Payload=mock.ANY
        )

    @patch('boto3.client')
    def test_handler_failure(self, mock_boto3_client):
        # Mock event data for the log file upload
        event = {
            'body': 'Sample log data',
        }

        # Mock context data
        context = MagicMock()

        # Mock environment variables
        os.environ['UNCOMPRESSED_BUCKET'] = 'uncompressed-bucket'
        os.environ['COMPRESS_LAMBDA_ARN'] = 'arn:aws:lambda:us-east-1:123456789012:function:compress-lambda-function'

        # Mock S3 client
        s3_mock = MagicMock()
        s3_mock.put_object.side_effect = Exception('Error storing object in S3')
        mock_boto3_client.return_value = s3_mock

        # Invoke the handler function
        response = handler(event, context)

        # Check if the response status code is 500
        self.assertEqual(response['statusCode'], 500)

        # Check if the response body contains the error message
        self.assertIn('Error storing object in S3', response['body'])


if __name__ == '__main__':
    unittest.main()
