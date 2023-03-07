import json
from pprint import pprint


# import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # TODO: add an authentication middleware layer before request routing happens
    

    # route the request
    pprint(event, indent=2)

    path: str = event['path']
    method = event['httpMethod']

    if path == '/hello':
        message = 'hello world from gracies eats backend!'
    elif path.startswith('/users') and '/recipes' not in path:
        user_id = event['pathParameters']['user_name']
    elif '/recipes' in path:
        # handle recipe endpoints
        pass
    else:
        message = 'not matched'

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f'message: {message}, method: {method}',
        }),
    }
