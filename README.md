
# Log File Upload System with AWS CDK

This project implements a system for uploading log files, compressing them, and storing them in AWS S3 using AWS CDK (Cloud Development Kit). The system consists of several components:

- **API Gateway:** Accepts HTTP POST requests with log file content.
- **Lambda Function (Process):** Processes the log file content and stores it in S3.
- **Lambda Function (Compress):** Compresses the log file and stores the compressed version in S3.
- **S3 Buckets:** One bucket for storing uncompressed log files and another for storing compressed log files.

## Components:

### API Gateway:
The API Gateway acts as the entry point for log file uploads. It accepts HTTP POST requests with log file content in the request body and forwards them to the Process Lambda function for processing.

### Lambda Function (Process):
The Process Lambda function receives log file content from the API Gateway, stores the uncompressed log file in an S3 bucket, and triggers the Compress Lambda function to compress the log file.

### Lambda Function (Compress):
The Compress Lambda function is triggered by the Process Lambda function. It compresses the log file stored in S3 and stores the compressed version in another S3 bucket.

### S3 Buckets:
Two S3 buckets are used to store log files:
- One bucket for storing uncompressed log files.
- Another bucket for storing compressed log files.

## Deployment Instructions:

1. Clone this repository to your local machine.

2. Install the AWS CDK CLI if you haven't already: 

```
$ npm install -g aws-cdk
```

3. Navigate to the root directory of the cloned repository.

4. Create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

4. Install project dependencies:

```
$ pip install -r requirements.txt
```

5. Deploy the infrastructure using AWS CDK:

6. Follow the prompts to deploy the stack. Once deployed, the AWS CDK will provide the endpoints for the API Gateway.

## Testing Instructions:

To test the system, you can use tools like cURL or Postman to send HTTP POST requests with log file content to the API Gateway endpoint.

Example cURL command:
```
curl -X POST -H "Content-Type: text/plain" -d "Your log file content here" <API Gateway Endpoint URL>
```

After uploading a log file, you can verify that the uncompressed and compressed versions are stored in the respective S3 buckets using the AWS Management Console or AWS CLI.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation