import botocore
import boto3
import json
from os import environ
from functools import lru_cache
s3_client = boto3.client('s3')

HOST_OVERRIDE = environ.get('HOST_OVERRIDE')
BUCKET_OVERRIDE = environ.get('BUCKET_OVERRIDE')
MAPPINGS_FILENAME = 'mappings.json'
CACHE_COUNT = int(environ.get('CACHE_COUNT')) or 0

@lru_cache(maxsize=CACHE_COUNT)
def read_host_mappings():
    print('Reading host mapping file')
    with open(MAPPINGS_FILENAME) as mappings_file:
        mappings = json.load(mappings_file)
        return mappings


@lru_cache(maxsize=CACHE_COUNT)
def get_bucket_content(bucket, path):
    if path.startswith('/'):
        key = path[1:]
    else:
        key = path
    print(f'Reading {key} from {bucket}')
    try:
        return s3_client.get_object(
            Bucket=bucket,
            Key=key,
        )
    except botocore.exceptions.ClientError as e:
        print(e)

def lambda_handler(event, context):
    if 'headers' not in event or 'host' not in event['headers']:
        return 'Invalid invocation'

    host = event['headers']['host']
    path = event['path']

    if path == '/' or path == '':
        path = '/index.html'

    if HOST_OVERRIDE and BUCKET_OVERRIDE:
        host_mappings = {
            HOST_OVERRIDE: BUCKET_OVERRIDE,
        }
    else:
        host_mappings = read_host_mappings()

    if host in host_mappings.keys():
        bucket_name = host_mappings[host]
        content = get_bucket_content(bucket_name, path)
        if content:
            print(f'Returning content {host} -> {bucket_name}{path}')
            content_body = content['Body'].read().decode('utf-8')
            return {
                'statusCode': 200,
                'isBase64Encoded': 'ContentType' in content and 'image/' in content['ContentType'],
                'headers': {
                    'Content-Type': content['ContentType'],
                },
                'body': content_body,
            }
        else:
            print(f'Content not found: {bucket_name}{path}')
    else:
        print(f'Host not found: {host}')
    return {
        'statusCode': 404,
        'statusDescription': '404 Not Found',
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': '<p>Not found</p>'
    }
