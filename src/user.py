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
    res = client.get_item(
        TableName='GraciesEats',
        Key={
            'PK': {'S': f'USER#{user_id}'},
            'SK': {'S': f'USER#{user_id}'},
        }
    )
    print('res: ')
    pprint(res)
    if 'Item' in res:
        item = res['Item']
        user = {
            'email': item['Email']['S'],
            'firstName': item['FirstName']['S'],
            'lastName': item['LastName']['S'],
        }
        message = f'Retrieved user {user_id}!'
    else:
        user = {}
        message = f'User {user_id} could not be found!'
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
            "user": user
        }),
    }


def create_user(user_id, payload):
    payload = json.loads(payload)
    message = f'Creating user {user_id}...'
    pprint(payload)
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
        # ConditionExpression = 'atrribute_notexists(#email)',
        # ExpressionAttributeNames = {
        #     "#email": "Email"
        # }
    )
    print(res)
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