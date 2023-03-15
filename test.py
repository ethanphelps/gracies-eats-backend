from pprint import pprint

# def prettify_recipe(recipe):
#     res = {}
#     for key in recipe.keys():
#         item = recipe[key]
#         if dynamo_type(item) == 'S' or dynamo_type(item) == 'BOOL':
#             res[key] = list(item.values())[0]
#         elif dynamo_type(item) == 'N':
#             res[key] = int(list(item.values())[0])
#         elif dynamo_type(item) == 'L':
#             res[key] = prettify_dynamo_list(list(item.values())[0])
#     return res


# list analog of prettify_dynamo_object
def prettify_dynamo_list(dynamo_list):
    res = []
    for item in dynamo_list:
        if dynamo_type(item) == 'S' or dynamo_type(item) == 'BOOL':
            res.append(dynamo_value(item))
        elif dynamo_type(item) == 'N':
            res.append(int(dynamo_value(item)))
        elif dynamo_type(item) == 'L':
            res.append(prettify_dynamo_list(dynamo_value(item)))
        elif dynamo_type(item) == 'M':
            res.append(prettify_dynamo_object(dynamo_value(item)))
    return res


# strips dynamo db type identifiers out of response objects, making it much easier to work with response data
# works recursively on nested objects and lists
# does NOT work with types Binary, Sets (all 3) or Null
def prettify_dynamo_object(dynamo_obj):
    res = {}
    for key in dynamo_obj.keys():
        item = dynamo_obj[key]
        if dynamo_type(item) == 'S' or dynamo_type(item) == 'BOOL':
            res[key] = dynamo_value(item)
        elif dynamo_type(item) == 'N':
            res[key] = int(dynamo_value(item))
        elif dynamo_type(item) == 'L':
            res[key] = prettify_dynamo_list(dynamo_value(item))
        elif dynamo_type(item) == 'M':
            res[key] = prettify_dynamo_object(dynamo_value(item))
    return res


def dynamo_type(dynamo_obj):
    return list(dynamo_obj.keys())[0]

def dynamo_value(dynamo_obj):
    return list(dynamo_obj.values())[0]


def test_prettify_recipe():
    test_obj = {
        "CookTime": {"S": "30 minutes"},
        "Description": {
            "S": "A refreshing and healthy smoothie made with fresh " "berries!"
        },
        "Id": {"S": "01GVHGZ77TQY45R03PKRK460T7"},
        "Ingredients": {
            "L": [
                {"M": {"name": {"S": "Mixed Berries"}, "quantity": {"N": "2"}}},
                {"M": {"name": {"S": "Banana"}, "quantity": {"N": "1"}}},
                {"M": {"name": {"S": "Yogurt"}, "quantity": {"N": "1"}}},
                {"M": {"name": {"S": "Honey"}, "quantity": {"N": "1"}}},
            ]
        },
        "Instructions": {
            "L": [
                {
                    "M": {
                        "description": {
                            "S": "Combine all ingredients "
                            "in a blender and blend "
                            "until smooth."
                        },
                        "prePrep": {"BOOL": False},
                    }
                },
                {
                    "M": {
                        "description": {"S": "Pour into glasses and " "enjoy!"},
                        "prePrep": {"BOOL": False},
                    }
                },
            ]
        },
        "Name": {"S": "Berry Smoothie"},
        "PK": {"S": "USER#ethanrphelps@yahoo.com"},
        "PrepTime": {"S": "10 minutes"},
        "SK": {"S": "RECIPE#01GVHGZ77TQY45R03PKRK460T7"},
        "Serves": {"N": "2"},
    }
    pprint(prettify_dynamo_object(test_obj))


if __name__ == '__main__':
    test_prettify_recipe()