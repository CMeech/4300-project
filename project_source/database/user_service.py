from project_source.database.queries import get_users, register_user, user_exists


class UserService():
    def get_client_list(self):
        data = get_users()
        return data

    def get_or_create(self, username):
        exists = user_exists(username)
        if not exists:
            register_user(username)