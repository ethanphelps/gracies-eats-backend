import boto3
import json
import ulid
from pprint import pprint
from models import Recipe
from utils import response, prettify_dynamo_object

client = boto3.client("dynamodb")


# call corresponding functions based param values and http method
def recipe_handler(event, path: str, method: str):
    pprint(event)
    user_id = event["pathParameters"]["user_name"]
    recipe_id = event["pathParameters"].get("recipe_id", None)
    body = event.get("body", {})
    payload = json.loads(body) if body else body
    print("payload:")
    print(payload)

    if recipe_id:
        if method == "GET":
            return get_recipe(user_id, recipe_id)
        elif method == "PUT":
            return update_recipe(user_id, recipe_id, payload)
        elif method == "DELETE":
            return delete_recipe(user_id, recipe_id)
    else:
        if method == "GET":
            return get_recipes(user_id)
        elif method == "POST":
            print("create recipe!!!")
            return create_recipe(user_id, payload)


def get_recipes(user_id):
    print(f"Getting recipes for user {user_id}")
    try:
        res = client.query(
            TableName="GraciesEats",
            KeyConditionExpression=f"#pk = :user_id AND begins_with(#sk, :sk_prefix)",
            ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
            ExpressionAttributeValues={
                ":user_id": {"S": f"USER#{user_id}"},
                ":sk_prefix": {"S": "RECIPE#"},
            },
        )
        pprint(res)
        recipes = [prettify_dynamo_object(recipe) for recipe in res['Items']]
        return response(200, recipes)
    except Exception as e:
        print(f"Exception occured: {e}")
        return response(400, f"Exception occurred: {e}")


# creates recipe with primary key format: USER#email, RECIPE#ulid
def create_recipe(user_id, recipe_data):
    print(f"Creating recipe for {user_id}!")
    if not recipe_data:
        return response(400, {"message": "Recipe data not sent!"})

    # validate schema
    try:
        recipe = Recipe(**recipe_data)
    except Exception as e:
        print(f"Validation error: {e}")
        return response(400, {"message": f"Validation error: {e}"})

    recipe_id = ulid.new()
    print(f"New recipe ID: {recipe_id}")

    # format ingredients and instructions lists
    ingredient_list = [
        {
            "M": {
                "name": {"S": ingredient.name},
                "quantity": {"N": str(ingredient.quantity)},
            }
        }
        for ingredient in recipe.ingredients
    ]
    instruction_list = [
        {
            "M": {
                "description": {"S": instruction.description},
                "prePrep": {"BOOL": instruction.prePrep},
            }
        }
        for instruction in recipe.instructions
    ]

    # write recipe
    try:
        res = client.put_item(
            TableName="GraciesEats",
            Item={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": f"RECIPE#{str(recipe_id)}"},
                "Id": {"S": str(recipe_id)},
                "Name": {"S": recipe.name},
                "Description": {"S": recipe.description},
                "PrepTime": {"S": recipe.prepTime},
                "CookTime": {"S": recipe.cookTime},
                "Serves": {"N": str(recipe.serves)},
                "Ingredients": {"L": ingredient_list},
                "Instructions": {"L": instruction_list},
            },
        )
        print(res)
        return response(
            201,
            {
                "message": f"Created recipe {str(recipe_id)}!",
                "recipeId": str(recipe_id),
            },
        )
    except Exception as e:
        return response(
            400,
            {"message": f"An exception of type {type(e).__name__} occurred: {str(e)}"},
        )


def get_recipe(user_id, recipe_id):
    print(f"Getting recipe {recipe_id} for user {user_id}")
    try:
        res = client.query(
            TableName="GraciesEats",
            KeyConditionExpression=f"#pk = :user_id AND #sk = :recipe_id",
            ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
            ExpressionAttributeValues={
                ":user_id": {"S": f"USER#{user_id}"},
                ":recipe_id": {"S": f"RECIPE#{recipe_id}"},
            },
        )
        pprint(res)
        recipes = [prettify_dynamo_object(recipe) for recipe in res['Items']]
        if recipes:
            return response(200, recipes)
        else:
            return response(404, {'message': f'Recipe {recipe_id} not found.'})
    except Exception as e:
        print(f"Exception occured: {e}")
        return response(400, f"Exception occurred: {e}")


# TODO: make generic update function or create specific ones for different updates
def update_recipe(user_id, recipe_id, recipe_data):
    print(f'Updating recipe {recipe_id} for user {user_id}')
    try:
        res = client.update_item(
            TableName='GraciesEats',
            Key={
                'PK': {'S': f'USER#{user_id}'},
                'SK': {'S': f'RECIPE#{recipe_id}'},
            },
            UpdateExpression='',
            ExpressionAttributeNames={},
            ExpressionAttributeValues={}
        )
        pprint(res)
    except Exception as e:
        print(f"Exception occured: {e}")
        return response(400, f"Exception occurred: {e}")


def delete_recipe(user_id, recipe_id):
    print(f"Deleting recipe {recipe_id} for user {user_id}")
    try:
        res = client.delete_item(
            TableName="GraciesEats",
            Key={
                'PK': {'S': f'USER#{user_id}'},
                'SK': {'S': f'RECIPE#{recipe_id}'},
            },
        )
        pprint(res)
        return response(200, {'message': f'Deleted recipe {recipe_id}'})
    except Exception as e:
        print(f"Exception occured: {e}")
        return response(400, f"Exception occurred: {e}")