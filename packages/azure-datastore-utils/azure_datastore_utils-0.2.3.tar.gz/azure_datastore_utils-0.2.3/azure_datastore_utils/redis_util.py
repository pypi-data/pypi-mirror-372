import json
import os

from typing import Literal

from redis import Redis
from redis_entraid.cred_provider import create_from_service_principal

RedisAuthStrategy = Literal['Password', 'ServicePrincipal', 'ManagedIdentity']
"""
Redis Authentication Strategy
    - Password means you authenticate with REDIS_PASSWORD in the environment variable
    - ServicePrincipal and ManagedIdentity means you need to set the 
    AZURE_TENANT_ID, AZURE_CLIENT_ID & AZURE_CLIENT_SECRET environment variables 
"""


class RedisUtil:
    """Utility class for interacting with Redis to store, retrieve, and manage cached data.

    We need the REDIS_HOST and REDIS_PORT environment variables defined before using this class

    This class provides helper methods to:
      - Authenticate with Redis using multiple strategies.
      - Set and get raw string or JSON values.
      - Manage list operations (push, range).
      - Perform increment/decrement counters.
      - Check existence of keys and manage expiration.

    Attributes:
        redis_client (Redis): Redis client connection instance.
    """

    def __init__(self, auth_strategy: RedisAuthStrategy = 'Password'):
        """Initializes the RedisUtil instance.

        Args:
            auth_strategy (RedisAuthStrategy): Authentication method to connect to Redis.
                Supported values are: "Password", "ServicePrincipal", "ManagedIdentity".
        """
        self.redis_client = RedisUtil.__get_client(auth_strategy)

    @staticmethod
    def __get_client(auth_strategy: RedisAuthStrategy):
        """Creates and returns a Redis client based on the authentication strategy.

        Args:
            auth_strategy (RedisAuthStrategy): Authentication method to connect to Redis.

        Returns:
            Redis: Configured Redis client instance.
        """
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = int(os.environ.get('REDIS_PORT', "6380"))

        if auth_strategy == 'Password':
            redis_password = os.environ.get('REDIS_PASSWORD')
            client = Redis(host=redis_host, port=redis_port, password=redis_password, ssl=True)
            return client
        elif auth_strategy == 'ServicePrincipal':
            credential_provider = RedisUtil.get_credential()
            client = Redis(host=redis_host, port=redis_port, credential_provider=credential_provider, ssl=True)
            return client
        return None

    @staticmethod
    def get_credential():
        """Retrieves Azure service principal credentials for Redis authentication.

        Returns:
            Any: Credential provider created from service principal.
        """
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        client_tenant_id = os.environ.get("AZURE_TENANT_ID")
        credential_provider = create_from_service_principal(client_id, client_secret, client_tenant_id)
        return credential_provider

    def set(self, key, value, expiration=None):
        """Sets a string value in Redis for the specified key.

        Args:
            key (str): The key under which the value is stored.
            value (str): The value to store.
            expiration (int, optional): Expiration time in seconds. Defaults to None.

        Returns:
            RedisUtil: Self instance for chaining.
        """
        value_to_store = value
        if value is None:
            value_to_store = ""
        value_to_store = value_to_store.encode('utf-8')
        self.redis_client.set(key, value_to_store, ex=expiration)
        return self

    def set_json(self, key, value, expiration=None):
        """Sets a JSON-serialized value in Redis.

        Args:
            key (str): The key under which the value is stored.
            value (Any): Python object to be serialized into JSON.
            expiration (int, optional): Expiration time in seconds. Defaults to None.

        Returns:
            RedisUtil: Self instance for chaining.
        """
        value_to_serialize = json.dumps(value)
        return self.set(key, value_to_serialize, expiration)

    def get(self, key):
        """Retrieves a string value from Redis.

        Args:
            key (str): The key whose value to retrieve.

        Returns:
            str | None: The value if found, otherwise None.
        """
        return_value = self.redis_client.get(key)
        if return_value is None:
            return None
        else:
            return return_value.decode("utf-8")

    def get_json(self, key: str):
        """Retrieves and deserializes a JSON value from Redis.

        Args:
            key (str): The key whose value to retrieve.

        Returns:
            dict: Deserialized JSON object. Returns empty dict if not found.
        """
        serialized_value = self.get(key)
        if serialized_value is None or serialized_value == "":
            serialized_value = '{}'
        de_serialized_value = json.loads(serialized_value)
        return de_serialized_value

    def delete(self, key):
        """Deletes a key from Redis.

        Args:
            key (str): The key to delete.
        """
        self.redis_client.delete(key)

    def l_push(self, key, values):
        """Pushes values to the head of a Redis list.

        Args:
            key (str): The list key.
            values (Any): Value(s) to push.

        Returns:
            RedisUtil: Self instance for chaining.
        """
        self.redis_client.lpush(key, values)
        return self

    def l_range(self, key, start, end):
        """Retrieves a range of values from a Redis list.

        Args:
            key (str): The list key.
            start (int): Starting index.
            end (int): Ending index.

        Returns:
            list: List of retrieved values.
        """
        return self.redis_client.lrange(key, start, end)

    def r_push(self, key, values):
        """Pushes values to the tail of a Redis list.

        Args:
            key (str): The list key.
            values (Any): Value(s) to push.

        Returns:
            RedisUtil: Self instance for chaining.
        """
        self.redis_client.rpush(key, values)
        return self

    def r_push_json(self, key, values):
        """Pushes JSON-serialized values to the tail of a Redis list.

        Args:
            key (str): The list key.
            values (Any): Python object to be serialized.

        Returns:
            RedisUtil: Self instance for chaining.
        """
        value_to_serialize = json.dumps(values)
        return self.r_push(key, value_to_serialize)

    def l_push_json(self, key, values):
        """Pushes JSON-serialized values to the head of a Redis list.

        Args:
           key (str): The list key.
           values (Any): Python object to be serialized.

        Returns:
           RedisUtil: Self instance for chaining.
        """
        value_to_serialize = json.dumps(values)
        return self.l_push(key, value_to_serialize)

    def l_range_json(self, key, start, end):
        """Retrieves and deserializes a range of JSON values from a Redis list.

        Args:
            key (str): The list key.
            start (int): Starting index.
            end (int): Ending index.

        Returns:
            list: List of deserialized JSON objects.
        """
        serialized_values = self.l_range(key, start, end)
        deserialized_values: list = []
        for serialized_value in serialized_values:
            deserialized_value = json.loads(serialized_value)
            deserialized_values.append(deserialized_value)
        return deserialized_values

    def l_range_all(self, key):
        """Retrieves all values from a Redis list.

        Args:
            key (str): The list key.

        Returns:
            list: List of all values.
        """
        return self.l_range(key, 0, -1)

    def l_range_json_all(self, key):
        """Retrieves and deserializes all JSON values from a Redis list.

        Args:
            key (str): The list key.

        Returns:
            list: List of deserialized JSON objects.
        """
        return self.l_range_json(key, 0, -1)

    def increment(self, key, increment_amount: int = 1) -> int:
        """Increments a key by a specified integer amount.

         If no key exists, the value will be initialized as amount

        Args:
            key (str): The key to increment.
            increment_amount (int, optional): Amount to increment by. Defaults to 1.

        Returns:
            int: New value after increment.
        """
        return self.redis_client.incrby(key, increment_amount)

    def increment_float(self, key, increment_amount: float = 1.0) -> float:
        """Increments a key by a specified float amount.

        If no key exists, the value will be initialized as amount

        Args:
            key (str): The key to increment.
            increment_amount (float, optional): Amount to increment by. Defaults to 1.0.

        Returns:
            float: New value after increment.
        """
        return self.redis_client.incrbyfloat(key, increment_amount)

    def decrement(self, key, decrement_amount: int = 1):
        """Decrements a key by a specified integer amount.

        If no key exists, the value will be initialized as 0

        Args:
            key (str): The key to decrement.
            decrement_amount (int, optional): Amount to decrement by. Defaults to 1.

        Returns:
            int: New value after decrement.
        """
        return self.redis_client.decrby(key, decrement_amount)

    def decrement_float(self, key, decrement_amount: float = 1.0):
        """Decrements a key by a specified float amount.

        If no key exists, the value will be initialized as 0

        Args:
            key (str): The key to decrement.
            decrement_amount (float, optional): Amount to decrement by. Defaults to 1.0.

        Returns:
            float: New value after decrement.
        """
        return self.redis_client.incrbyfloat(key, (decrement_amount * -1.0))

    def exists(self, key):
        """Checks if a key exists in Redis.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        result = self.redis_client.exists(key)
        if result:
            return True
        return False

    def expire(self, key: str, time: int):
        """Sets an expiration time for a key.

        Args:
            key (str): The key to expire.
            time (int): Expiration time in seconds.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self.redis_client.expire(key, time)

    def set_expire(self, key, value: str, time: int):
        """Sets a key with a value and expiration time in one operation.

        Args:
            key (str): The key to set.
            value (str): The value to set.
            time (int): Expiration time in seconds.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self.redis_client.setex(key, time, value)
