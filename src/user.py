import boto3
import json
from pprint import pprint

client = boto3.client('dynamodb')

def user_handler(event, path: str, method: str):
    user_id = event['pathParameters']['user_name']
    # call corresponding functions based param values and http method
    if method == 'GET':
        return get_user(user_id)
    elif method == 'POST':
        return create_user(user_id, event['body'])
    elif method == 'PUT':
        return update_user(user_id, event['body'])
    else:
        return {
            "statusCode": 404
        }


def get_user(user_id):
    message = f'Getting user {user_id}...'
    paginator = client.get_paginator('list_tables')
    response_iterator = paginator.paginate(
        PaginationConfig={
            'MaxItems': 100,
            'Pagesize': 100
        }
    )
    print(response_iterator)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f'Retrieved user {user_id}!',
        }),
    }


def create_user(user_id, payload):
    message = f'Creating user {user_id}...'
    pprint(json.loads(payload))
    email = payload['email']
    first_name = payload['firstName']
    last_name = payload['lastName']
    res = client.put_item(
        TableName = 'GraciesEats',
        Item = {
            "PK": { "S": f'USER#{email}' },
            "SK": { "S": f'USER#{email}' },
            "Email": { "S": email },
            "FirstName": { "S": first_name },
            "LastName": { "S": last_name },
        },
        ConditionExpression: 'atrribute_notexists(#email)',
        ExpressionAttributeNames = {
            "#email": "Email"
        }
    )
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f'Created user {user_id}!',
        }),
    }


def update_user(user_id, payload):
    message = f'Updating user {user_id}...'
    pprint(json.loads(payload))
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f'Updated user {user_id}!',
        }),
    }