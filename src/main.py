import os

import boto3
import requests
from remotezip import RemoteZip
from aws_requests_auth.aws_auth import AWSRequestsAuth


response = requests.get('https://sentinel1.asf.alaska.edu/s3credentials')
response.raise_for_status()
credentials = response.json()

auth = AWSRequestsAuth(
    aws_service='s3',
    aws_host='s3-us-west-2.amazonaws.com',
    aws_region='us-west-2',
    aws_access_key=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_token=credentials['SessionToken'],
)

s3 = boto3.client('s3')
target_bucket = 'asj-dev'


def process_granules(granules):
    for granule in granules:
        print(granule)
        url = f'https://s3-us-west-2.amazonaws.com/asf-ngap2w-p-s1-slc-7b420b89/{granule}.zip'
        with RemoteZip(url, auth=auth) as z:
            filenames = z.namelist()
            for filename in filenames:
                if filename.endswith('.xml') or filename.endswith('.safe'):
                    print(filename)
                    z.extract(filename)
                    s3.upload_file(filename, target_bucket, filename)
                    os.remove(filename)


def lambda_handler(event, context):
    granules = [record['body'] for record in event['Records']]
    process_granules(granules)
