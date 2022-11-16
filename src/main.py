import os

import boto3
import requests
from remotezip import RemoteZip
from aws_requests_auth.aws_auth import AWSRequestsAuth


s3 = boto3.client('s3')


def get_auth():
    response = requests.get(
        'https://urs.earthdata.nasa.gov/oauth/authorize?client_id=BO_n7nTIlMljdvU6kRRB3g&response_type=code&redirect_uri=https://sentinel1.asf.alaska.edu/login&state=%2Fs3credentials&app_type=401',
        auth=(os.environ['USERNAME'], os.environ['PASSWORD']),
    )
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
    return auth


def process_granules(granules):
    auth = get_auth()
    for granule in granules:
        print(granule)
        url = f'https://s3-us-west-2.amazonaws.com/asf-ngap2w-p-s1-slc-7b420b89/{granule}.zip'
        with RemoteZip(url, auth=auth) as z:
            filenames = z.namelist()
            for filename in filenames:
                if filename.endswith('.xml') or filename.endswith('.safe'):
                    z.extract(filename)
                    s3.upload_file(filename, os.environ['BUCKET'], filename)
                    os.remove(filename)


def lambda_handler(event, context):
    granules = [record['body'] for record in event['Records']]
    os.chdir('/tmp')
    process_granules(granules)
