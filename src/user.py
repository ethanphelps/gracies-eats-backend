def user_handler(user_id: str, method: str):
    # call corresponding functions based param values and http method
    if method == 'GET':
        message = f'Getting user {user_id}...'
    elif method == 'POST':
        message = f'Creating user {user_id}...'
    elif method == 'PUT':
        message = f'Updating user {user_id}...'
    pass