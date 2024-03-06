import os
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from compress import handler


class TestHandler(unittest.TestCase):

    patch_boto3_client = patch('boto3.client')
    mock_boto3_client = patch_boto3_client.start()

    def test_handler(self):
        # Mock event data for the log file upload
        event = {
            'timestamp': '2022-01-01T00:00:00Z',
            'content': 'Sample log data',
        }

        # Mock context data
        context = MagicMock()

        # Mock environment variables
        os.environ['COMPRESSED_BUCKET'] = 'compressed-bucket'

        # Mock S3 client
        s3_mock = MagicMock()
        s3_mock.put_object.side_effect = [{}, Exception('Error storing object in S3')]
        self.mock_boto3_client.return_value = s3_mock

        # Invoke the handler function with success mocks
        response = handler(event, context)

        # Check if the response is successful
        self.assertEqual(response['statusCode'], 200)

        # Check if the response body contains the expected message
        self.assertEqual(response['body'], 'Log file compressed and stored successfully')

        # Check if the object was stored in the S3 bucket
        s3_mock.put_object.assert_called_once_with(Bucket='compressed-bucket', Key="log_file_2022-01-01T00:00:00Z.txt.gz", Body=mock.ANY)


    # Test failure
        # Invoke the handler function with failure mock
        response = handler(event, context)

        # Check if the response status code is 500
        self.assertEqual(response['statusCode'], 500)

        # Check if the response body contains the error message
        self.assertIn('Error storing object in S3', response['body'])


if __name__ == '__main__':
    unittest.main()
