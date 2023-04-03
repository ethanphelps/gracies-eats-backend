import boto3
import json
import ulid
from pprint import pprint
from models import Recipe
from utils import response, prettify_dynamo_object
import fields
import base64

client = boto3.client("dynamodb")
s3_client = boto3.client("s3")


# call corresponding functions based param values and http method
def recipe_handler(event, path: str, method: str):
    pprint(event)
    user_id = event["pathParameters"]["user_name"]
    recipe_id = event["pathParameters"].get("recipe_id", None)
    body = event.get("body", {})

    if recipe_id:
        if method == "GET":
            return get_recipe(user_id, recipe_id)
        elif method == "PUT":
            return update_recipe(user_id, recipe_id, body)
        elif method == "DELETE":
            return delete_recipe(user_id, recipe_id)
    else:
        if method == "GET":
            return get_recipes(user_id)
        elif method == "POST":
            print("create recipe!!!")
            return create_recipe(user_id, body)


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
# returns a pre-signed url for uploading cover image to S3
def create_recipe(user_id, recipe_data):
    print(f"Creating recipe for {user_id}!")
    if not recipe_data:
        return response(400, {"message": "Recipe data not sent!"})

    recipe_data = json.loads(recipe_data) if recipe_data else recipe_data
    print("recipe_data:")
    print(recipe_data)

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
                fields.INGREDIENT_NAME: {"S": ingredient.name},
                fields.INGREDIENT_QUANTITY: {"N": str(ingredient.quantity)},
            }
        }
        for ingredient in recipe.ingredients
    ]
    instruction_list = [
        {
            "M": {
                fields.INSTRUCTION_DESCRIPTION: {"S": instruction.description},
                fields.INSTRUCTION_PREPREP: {"BOOL": instruction.prePrep},
            }
        }
        for instruction in recipe.instructions
    ]


    # create presigned url for cover image upload and send to UI
    try:
        presigned_url_data = s3_client.generate_presigned_post(
            Bucket='gracies-eats-recipe-images',
            Key=f'{user_id}/{recipe_id}',
            ExpiresIn=30
        )
        pprint(presigned_url_data)
    except Exception as e:
        return response(
            500,
            {"message": f"An exception of type {type(e).__name__} occurred: {str(e)}"},
        )

    image_url = presigned_url_data['url'] + presigned_url_data['fields']['key']
    print(f'Image url: {image_url}')

    # write recipe
    try:
        res = client.put_item(
            TableName="GraciesEats",
            Item={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": f"RECIPE#{str(recipe_id)}"},
                fields.ID: {"S": str(recipe_id)},
                fields.NAME: {"S": recipe.name},
                fields.DESCRIPTION: {"S": recipe.description},
                fields.PREP_TIME: {"S": recipe.prepTime},
                fields.COOK_TIME: {"S": recipe.cookTime},
                fields.SERVES: {"N": str(recipe.serves)},
                fields.INGREDIENTS: {"L": ingredient_list},
                fields.INSTRUCTIONS: {"L": instruction_list},
                fields.IMAGE_URL: {"S": image_url}
            },
        )
        print(res)
        return response(
            201,
            {
                "message": f"Created recipe {str(recipe_id)}!",
                "recipeId": str(recipe_id),
                "presignedUrlData": presigned_url_data
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
        if res['Items']:
            recipe = prettify_dynamo_object(res['Items'][0])
            return response(200, recipe)
        else:
            return response(404, {'message': f'Recipe {recipe_id} not found.'})
    except Exception as e:
        print(f"Exception occured: {e}")
        return response(400, f"Exception occurred: {e}")


# TODO: make generic update function or create specific ones for different updates
def update_recipe(user_id, recipe_id, recipe_data):
    recipe_data = json.loads(recipe_data) if recipe_data else recipe_data
    print("recipe_data:")
    print(recipe_data)
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