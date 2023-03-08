import boto3
from pprint import pprint

client = boto3.client('dynamodb')
paginator = client.get_paginator('list_tables')
response_iterator = paginator.paginate(
    PaginationConfig={
        'MaxItems': 100,
        'Pagesize': 100
    }
)
for page in response_iterator:
    pprint(page)

print(response_iterator)