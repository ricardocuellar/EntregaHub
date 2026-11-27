def user_data(user):
    return {
        'id': user.pk,
        'username': user.username,
        'name': user.first_name or user.username,
        'role': user.role,
    }
