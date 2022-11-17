import os

import boto3
import remotezip
import requests
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


def process_granule(granule, session):
    print(granule)
    url = f'https://s3-us-west-2.amazonaws.com/asf-ngap2w-p-s1-slc-7b420b89/{granule}.zip'

    for ii in range(3):
        try:
            with remotezip.RemoteZip(url, session=session) as z:
                filenames = z.namelist()
                for filename in filenames:
                    if (filename.endswith('.xml') and '/calibration/' not in filename) or filename.endswith('.safe'):
                        with z.open(filename) as file_handle:
                            s3.upload_fileobj(file_handle, os.environ['BUCKET'], filename)
            return
        except remotezip.RemoteIOError:
            if ii == 2:
                raise


def process_granules(granules):
    session = requests.Session()
    session.auth = get_auth()

    for granule in granules:
        process_granule(granule, session)


def lambda_handler(event, context):
    granules = [record['body'] for record in event['Records']]
    process_granules(granules)
