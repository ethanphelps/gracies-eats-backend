import boto3
import json
import ulid
from pprint import pprint
from models import Recipe
from utils import response

client = boto3.client("dynamodb")


def recipe_handler(event, path: str, method: str):
    # call corresponding functions based param values and http method
    pprint(event)
    user_id = event['pathParameters']['user_name']
    recipe_id = event['pathParameters'].get('recipe_id', None)
    payload = json.loads(event.get('body', {}))
    print('payload:')
    print(payload)

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
    try:
        res = client.query(
            TableName='GraciesEats',
            KeyConditionExpression=f'#pk = {user_id} AND begins_with(#sk, :sk_prefix)',
            ExpressionAttributeNames={
                '#pk': 'PK',
                '#sk': 'SK'
            },
            ExpressionAtributeValues={
                ':sk_prefix': 'RECIPE#'
            }
        )
    except Exception as e:
        print(f'Exception occured: {e}')
        return response(400, f'Exception occurred: {e}')


def create_recipe(user_id, recipe_data):
    print(f'Creating recipe for {user_id}!')
    if not recipe_data:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Recipe data not sent!'
            })
        }
    # payload = json.loads(recipe_data)

    # validate schema
    try:
        recipe = Recipe(**recipe_data)
    except Exception as e:
        print(f'Validation error: {e}')
        return response(400, {
            'message': f'Validation error: {e}'
        })

    recipe_id = ulid.new() 
    print(f'New recipe ID: {recipe_id}')

    # format ingredients and instructions lists
    ingredient_list = [{
        'M': {
            'name': {'S': ingredient.name}, 
            'quantity': {'N': str(ingredient.quantity)}
        }} 
        for ingredient in recipe.ingredients
    ]
    # ingredients = {'L': ingredient_list}
    instruction_list = [{'M': {'description': {'S': instruction.description}, 'prePrep': {'BOOL': instruction.prePrep}}} for instruction in recipe.instructions]
    # instructions = {'L': instruction_list}

    # write recipe
    try:
        res = client.put_item(
            TableName='GraciesEats',
            Item={
                'PK': {'S': f'USER#{user_id}'},
                'SK': {'S': f'RECIPE#{str(recipe_id)}'},
                'Name': {'S': recipe.name},
                'Description': {'S': recipe.description},
                'PrepTime': {'S': recipe.prepTime},
                'CookTime': {'S': recipe.cookTime},
                'Serves': {'N': str(recipe.serves)},
                'Ingredients': {'L': ingredient_list},
                'Instructions': {'L': instruction_list}
            },
        )
        print(res)
        return response(201, {
            'message': f'Created recipe {str(recipe_id)}!',
            'recipeId': str(recipe_id)
        })
    except Exception as e:
        return response(400, {
            'message': f'An exception of type {type(e).__name__} occurred: {str(e)}'
        })


    # USER#email, RECIPE#ulid


def get_recipe(user_id, recipe_id):
    return


def update_recipe(user_id, recipe_id, recipe_data):
    pass