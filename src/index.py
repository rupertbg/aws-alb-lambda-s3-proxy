import botocore
import boto3
import json
s3_client = boto3.client("s3")

MAPPINGS_FILENAME = 'mappings.json'


def read_host_mappings():
    with open(MAPPINGS_FILENAME) as mappings_file:
        mappings = json.load(mappings_file)
        return mappings


def get_bucket_content(bucket, path):
    try:
        return s3_client.get_object(
            Bucket=bucket,
            Key=path,
        )['Body']
    except botocore.exceptions.ClientError as e:
        print(e.response['Error']['Code'])


def lambda_handler(event, context):
    if 'headers' not in event or 'host' not in event['headers']:
        return 'Invalid invocation'

    host = event['headers']['host']
    path = event['path']

    if path == '/' or path == '':
        path = '/index.html'

    host_mappings = read_host_mappings()

    if host in host_mappings.keys():
        bucket_name = host_mappings[host]
        content = get_bucket_content(bucket_name, path)
        return json.dumps({
            "statusCode": 200,
            "isBase64Encoded": 'image/' in content['ContentType'],
            "headers": {
                "Content-Type": content['ContentType'],
            },
            "body": content['Body'],
        })
    else:
        return json.dumps({
            "statusCode": 404,
            "statusDescription": "404 Not Found",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": "<p>Not found</p>"
        })
