# AWS_Lambda_Layer_Libs
AWS Lambda function on Python which allows to make a python.zip archive in your S3 bucket by given requirements.txt file

# Deploying:
Create an S3 bucket
Create a Lambda function (I used Python 3.9) with the code from Lambda-Layer-Download-Bulk.py
Attach role to Lambda with get/list/put permissions to your S3 bucket

Make sure your Lambda function have set maximum timeout limit and enough memory

# Usage:

Put requirements.txt file (or other file name) into the root of your S3 bucket containing libraries and version in the format:
```
aiobotocore==1.4.2
aiohttp==3.7.4.post0
aioitertools==0.8.0
```

Inside the Lambda function in #Parameters section put your S3 bucket name and the name of your txt file with the requirements

Run Lambda function
After it finished it should create a new date-time folder with a python.zip archive inside it with all the libraries from requirements.txt
It will also contain the original requirements.txt file inside that folder to be able to check which libraries are inside the archive in the future

Then you can create your Lambda layers using this python.zip file