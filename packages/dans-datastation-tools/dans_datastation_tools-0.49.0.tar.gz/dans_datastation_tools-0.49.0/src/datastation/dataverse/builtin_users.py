import requests

from datastation.common.utils import print_dry_run_message


class User:

    def __init__(self, user_name, first_name, last_name, email, affiliation, position, encrypted_password):
        self.username = user_name
        self.firstName = first_name
        self.lastName = last_name
        self.email = email
        self.affiliation = affiliation
        self.position = position
        self.encrypted_password = encrypted_password

    def to_json(self):
        return {"userName": self.username, "firstName": self.firstName, "lastName": self.lastName, "email": self.email,
                "affiliation": self.affiliation, "position": self.position}

    def get_encrypted_password(self):
        return self.encrypted_password

    def __str__(self):
        return f"User(username={self.username}, firstName={self.firstName}, lastName={self.lastName}, email={self.email}, " \
               f"affiliation={self.affiliation}, position={self.position}, encrypted_password={self.encrypted_password})"


class BuiltInUsersApi:

    def __init__(self, server_url, api_token, builtin_user_key, unblock_key=None):
        self.server_url = server_url
        self.api_token = api_token
        self.builtin_users_key = builtin_user_key
        self.unblock_key = unblock_key

    def create(self, user: User, initial_password="dummy1234",
               send_email_notification=False, dry_run=False):
        url = f"{self.server_url}/api/builtin-users"
        headers = {'X-Dataverse-key': self.api_token}
        params = {'key': self.builtin_users_key,
                  'sendEmailNotification': 'true' if send_email_notification else 'false',
                  'password': initial_password}
        if self.unblock_key:
            params['unblock-key'] = self.unblock_key

        if dry_run:
            print_dry_run_message(method='POST', url=url, headers=headers, params=params, json=user.to_json())
            return None
        else:
            return requests.post(url, headers=headers, params=params, json=user.to_json())
