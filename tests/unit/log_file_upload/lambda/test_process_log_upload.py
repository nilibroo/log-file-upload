import os
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from process import handler 

class TestHandler(unittest.TestCase):
    
    # All tests are in one def since s3 client is global and initialized once, 
    # so that's the way I found to mock it properly
    
    
    # Create a global patch for boto3.client
    patch_boto3_client = patch('boto3.client')
    mock_boto3_client = patch_boto3_client.start()


    def test_handler(self):
        
        # Mock s3 client
        s3_mock = MagicMock()
        s3_mock.put_object.side_effect = [{}, {}, Exception('Error storing object in S3')]

        # Mock lambda client
        lambda_mock_success = MagicMock()
        lambda_mock_failure = MagicMock()
        lambda_mock_success.invoke.return_value = {'Payload': MagicMock(read=lambda: '{"statusCode": 200}')}
        lambda_mock_failure.invoke.return_value = {'Payload': MagicMock(read=lambda: '{"statusCode": 500, "body": "Some compression error"}')}
        self.mock_boto3_client.side_effect = [s3_mock, lambda_mock_success, lambda_mock_failure]
        
      # Test success
        # Mock event data for the log file upload
        event = {
            'body': 'Sample log data',
        }

        # Mock context data
        context = MagicMock()

        # Mock environment variables
        os.environ['UNCOMPRESSED_BUCKET'] = 'uncompressed-bucket'
        os.environ['COMPRESS_LAMBDA_ARN'] = 'arn:aws:lambda:us-east-1:123456789012:function:compress-lambda-function'

        # Invoke the handler function with success mocks
        response = handler(event, context)

        # Check if the response is successful
        self.assertEqual(response['statusCode'], 200)

        # Check if the response body contains the expected message
        self.assertEqual(response['body'], '"Log file uploaded successfully"')

        # Check if the object was stored in the S3 bucket
        s3_mock.put_object.assert_called_once_with(Bucket='uncompressed-bucket', Key=mock.ANY, Body='Sample log data')

        # Check if the compress Lambda function was invoked
        lambda_mock_success.invoke.assert_called_once_with(
            FunctionName='arn:aws:lambda:us-east-1:123456789012:function:compress-lambda-function',
            InvocationType='RequestResponse',
            Payload=mock.ANY
        )

    # Test failure from compress lambda

        # Invoke the handler function with lambda filaure mock
        response = handler(event, context)

        # Check if the response is successful
        self.assertEqual(response['statusCode'], 500)

        # Check if the response body contains the expected message
        self.assertEqual(response['body'], '"Error from compress Lambda: Some compression error"')

        # Check if the object was stored in the S3 bucket
        s3_mock.put_object.assert_called_with(Bucket='uncompressed-bucket', Key=mock.ANY, Body='Sample log data')

        # Check if the compress Lambda function was invoked
        lambda_mock_failure.invoke.assert_called_once_with(
            FunctionName='arn:aws:lambda:us-east-1:123456789012:function:compress-lambda-function',
            InvocationType='RequestResponse',
            Payload=mock.ANY
        )

    # Test failure from S3

        # Invoke the handler function with ns3 failure mock
        response = handler(event, context)

        # Check if the response status code is 500
        self.assertEqual(response['statusCode'], 500)

        # Check if the response body contains the error message
        self.assertIn('Error storing object in S3', response['body'])


if __name__ == '__main__':
    unittest.main()
