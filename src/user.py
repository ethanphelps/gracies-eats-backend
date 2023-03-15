import boto3
import json
from pprint import pprint
from models import User
from utils import response

client = boto3.client("dynamodb")
paginator = client.get_paginator("scan")


def user_handler(event, path: str, method: str):
    # call corresponding functions based param values and http method
    if path == "/users":
        if method == "POST":
            return create_user(event["body"])
        elif method == "GET":
            return get_all_users()
    else:
        user_id = event["pathParameters"]["user_name"]
        if method == "GET":
            return get_user(user_id)
        elif method == "PUT":
            return update_user(user_id, event["body"])
        else:
            return {"statusCode": 404}


def get_user(user_id):
    message = f"Getting user {user_id}..."
    try:
        res = client.get_item(
            TableName="GraciesEats",
            Key={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": f"USER#{user_id}"},
            },
        )
        pprint(res)
        if "Item" in res:
            item = res["Item"]
            user = {
                "email": item["Email"]["S"],
                "firstName": item["FirstName"]["S"],
                "lastName": item["LastName"]["S"],
            }
            status = 200
            message = f"Retrieved user {user_id}!"
        else:
            status = 404
            user = {}
            message = f"User {user_id} could not be found!"
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": f"An exception of type {type(e).__name__} occurred: {str(e)}"
                }
            ),
        }

    return {
        "statusCode": status,
        "body": json.dumps({"message": message, "user": user}),
    }


def create_user(payload):
    payload = json.loads(payload)
    pprint(payload)

    # validate schema
    try:
        user = User(**payload)
    except Exception as e:
        print(f'Validation error: {e}')
        return response(400, {
            'message': f'Validation error: {e}'
        })

    # write to dynamodb 
    try:
        res = client.put_item(
            TableName="GraciesEats",
            Item={
                "PK": {"S": f"USER#{user.email}"},
                "SK": {"S": f"USER#{user.email}"},
                "Email": {"S": user.email},
                "FirstName": {"S": user.firstName},
                "LastName": {"S": user.lastName},
            },
            ConditionExpression="attribute_not_exists(#email)",
            ExpressionAttributeNames={"#email": "Email"},
        )
        print(res)
        return response(201, {
            'message': f'Created user {user.email}!'
        })
    except Exception as e:
        return response(400, {
            "message": f"An exception of type {type(e).__name__} occurred: {str(e)}"
        })


def update_user(user_id, payload):
    payload = json.loads(payload)
    pprint(payload)

    # validate user
    try:
        user = User(**payload)
    except Exception as e:
        print(f'Validation error: {e}')
        return response(400, {
            'message': f'Validation error: {e}'
        })

    # update user
    return response(200, {
        'message': f'Updated user {user_id}!',
    })


def get_all_users():
    try:
        response_iterator = paginator.paginate(
            TableName="GraciesEats",
            FilterExpression="contains(#pk, :value)",
            ExpressionAttributeNames={"#pk": "PK"},
            ExpressionAttributeValues={":value": {"S": "USER#"}},
            ProjectionExpression='Email'
        )
        users = []
        for page in response_iterator:
            for user in page['Items']:
                users.append(user['Email']['S'])
                # users.append(user)
                pprint(user)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "users": users
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": f"An exception of type {type(e).__name__} occurred: {str(e)}"
                }
            ),
        }
