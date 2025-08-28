"""This module handles generating and fetching constants and credentials from the database"""

from datetime import datetime

from mbu_dev_shared_components.utils.fernet_encryptor import Encryptor


class Constants:
    """Base class for adding and collection constants and credentials"""

    def add_constant(self, constant_name: str, value: str, changed_at: datetime = datetime.now()):
        query = """
            INSERT INTO [RPA].[rpa].[Constants] ([name], [value], [changed_at])
            VALUES (?, ?, ?)
        """
        self.execute_query(query, [constant_name, value, changed_at])

    def get_constant(self, constant_name: str) -> dict:
        query = """
            SELECT name, value FROM [RPA].[rpa].[Constants] WHERE name = ?
        """
        res = self.execute_query(query, [constant_name])
        if res:
            name, value = res[0]
            return {"constant_name": name, "value": value}
        raise ValueError(f"No constant found with name: {constant_name}")

    def add_credential(self, credential_name: str, username: str, password: str,
                       changed_at: datetime = datetime.now()):
        encryptor = Encryptor()
        encrypted_password = encryptor.encrypt(password)
        query = """
            INSERT INTO [RPA].[rpa].[Credentials] ([name], [username], [password], [changed_at])
            VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, [credential_name, username, encrypted_password, changed_at])

    def get_credential(self, credential_name: str) -> dict:
        encryptor = Encryptor()
        query = """
            SELECT username, CAST(password AS varbinary(max))
            FROM [RPA].[rpa].[Credentials]
            WHERE name = ?
        """
        res = self.execute_query(query, [credential_name])
        if res:
            username, encrypted_password = res[0]
            decrypted_password = encryptor.decrypt(encrypted_password)
            return {
                "username": username,
                "decrypted_password": decrypted_password,
                "encrypted_password": encrypted_password
            }
        raise ValueError(f"No credential found with name {credential_name}")
