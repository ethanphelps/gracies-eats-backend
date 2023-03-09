import boto3
from pprint import pprint

client = boto3.client('dynamodb')
# paginator = client.get_paginator('list_tables')
# response_iterator = paginator.paginate(
#     PaginationConfig={
#         'MaxItems': 100,
#         'Pagesize': 100
#     }
# )
# for page in response_iterator:
#     pprint(page)


# res = client.get_item(
#     TableName='GraciesEats',
#     Key={
#         'PK': {'S': 'USER#ethanrphelps@yahoo.com'},
#         'SK': {'S': 'USER#ethanrphelps@yahoo.com'},
#     }
# )
# pprint(res)
# print('---')
# pprint(res['Item'])

paginator = client.get_paginator("scan")

try:
    response_iterator = paginator.paginate(
        TableName="GraciesEats",
        FilterExpression="contains(#pk, :value)",
        ExpressionAttributeNames={"#pk": "PK"},
        ExpressionAttributeValues={':value': {'S': 'USER#'}},
    )
    for page in response_iterator:
        pprint(page)
except Exception as e:
    print(f'An exception of type {type(e).__name__} occurred: {str(e)}')