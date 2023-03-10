import boto3
import json
import ulid
from pprint import pprint

client = boto3.client("dynamodb")


def recipe_handler(event, path: str, method: str):
    # call corresponding functions based param values and http method
    pprint(event)
    user_id = event['pathParameters']['user_name']
    recipe_id = event['pathParameters'].get('recipe_id', None)
    payload = json.loads(event.get('body', {}))
    if recipe_id:
        if method == 'GET':
            return get_recipe(user_id, recipe_id)
        elif method == 'PUT':
            return update_recipe(user_id, recipe_id, payload)
    else:
        if method == 'GET':
            return get_recipes(user_id)
        elif method == 'POST':
            print('create recipe!!!')
            return create_recipe(user_id, payload)


def get_recipes(user_id):
    pass


def create_recipe(user_id, recipe_data):
    print(f'Creating recipe for {user_id}!')
    if not recipe_data:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Recipe data not sent!'
            })
        }

    recipe_id = ulid.new() 
    print(f'New recipe ID: {recipe_id}')
    return {
        'statusCode': 201,
        'body': json.dumps({
            'message': 'Recipe created!',
            'recipeId': str(recipe_id)
        })
    }

    # USER#email, RECIPE#ulid


def get_recipe(user_id, recipe_id):
    return


def update_recipe(user_id, recipe_id, recipe_data):
    pass