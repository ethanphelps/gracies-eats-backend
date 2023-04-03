import boto3
import json
from pprint import pprint
from models import User
from utils import response, prettify_dynamo_object
import fields

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
            user = prettify_dynamo_object(res['Item'])
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
                fields.EMAIL: {"S": user.email},
                fields.FIRST_NAME: {"S": user.firstName},
                fields.LAST_NAME: {"S": user.lastName},
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

    try:
        # get any fields that aren't a part of the model
        unrecognized_fields = []
        for key in payload.keys():
            if key not in User.__fields__.keys():
                unrecognized_fields.append(key)

        if len(unrecognized_fields) > 0:
            return response(400, {
                'message': f'Validation error: The following fields are not part of the user model: {unrecognized_fields}. Users can contain the following fields: {list(User.__fields__.keys())}'
            })

        # retrieve current value of user 
        res = client.get_item(
            TableName="GraciesEats",
            Key={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": f"USER#{user_id}"},
            },
        )
        if "Item" in res:
            user = prettify_dynamo_object(res['Item'])
        else:
            return response(404, {'message': f"User {user_id} could not be found!"})

        # update fields provided in the payload and validate result
        for field in list(payload.keys()):
            user[field] = payload[field]
        try:
            user = User(**user)
        except Exception as e:
            return response(400, { 'message': f'Validation error: {e}' })

        # create update expression
        # fields = list(payload.keys())
        # update_exp = f'{fields[0]} = {payload[fields[0]]}'
        # fields = fields[1:]
        # for field in fields:
        #     update_exp += f' AND {field} = {payload[field]}'
        update_exp = 'SET #email = :email, #firstName = :firstName, #lastName = :lastName'
        res = client.update_item(
            TableName='GraciesEats',
            Key={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": f"USER#{user_id}"},
            },
            UpdateExpression=update_exp,
            ExpressionAttributeNames={
                '#email': 'email',
                '#firstName': 'firstName',
                '#lastName': 'lastName',
            },
            ExpressionAttributeValues={
                ':email': {'S': user.email},
                ':firstName': {'S': user.firstName},
                ':lastName': {'S': user.lastName}
            },
            ReturnValues='ALL_NEW'
        )

        pprint(res)
    except Exception as e:
        # if isinstance(e, ValidationException):
        #     return response(400, { 'message': str(e) })
        # elif isinstance(e, NotFoundException):
        #     return response(404, { 'message': str(e) })
        # else:
        print(f'Error: {e}')
        return response(500, {
            'message': f'Internal Server Error: {e}'
        })

    # update user
    return response(200, {
        'message': f'Updated user {user_id}!',
    })


def get_all_users():
    try:
        response_iterator = paginator.paginate(
            TableName="GraciesEats",
            FilterExpression="contains(#pk, :value) AND contains(#sk, :value)",
            ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
            ExpressionAttributeValues={":value": {"S": "USER#"}},
            # ProjectionExpression='Email'
        )
        users = []
        for page in response_iterator:
            for user in page['Items']:
                users.append(prettify_dynamo_object(user))
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
