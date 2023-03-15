import json

def response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }


# strips dynamo db type identifiers out of response objects, making it much easier to work with response data
# works recursively on nested objects and lists
# does NOT work yet with types Binary, Sets (all 3) or Null
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


# extracts type of a field in a dynamo db response object
def dynamo_type(dynamo_obj):
    return list(dynamo_obj.keys())[0]


# extracts value of a field in a dynamo db response object
def dynamo_value(dynamo_obj):
    return list(dynamo_obj.values())[0]

