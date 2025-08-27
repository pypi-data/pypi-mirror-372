
import json
import os

from typing import Literal

from redis.asyncio import Redis
from redis_entraid.cred_provider import create_from_service_principal

from .redis_util import RedisAuthStrategy


class RedisAsyncUtil:
    """Utility class to handle interacting with Redis to store and retrieve cached data"""

    def __init__(self, auth_strategy: RedisAuthStrategy):
        """Initialize RedisUtil object"""
        self.redis_client = RedisAsyncUtil.__get_client(auth_strategy)

    @staticmethod
    def __get_client(auth_strategy: RedisAuthStrategy):
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = int(os.environ.get('REDIS_PORT', "6380"))

        if auth_strategy == 'Password':
            redis_password = os.environ.get('REDIS_PASSWORD')
            client = Redis(host=redis_host, port=redis_port, password=redis_password, ssl=True)
            return client
        elif auth_strategy == 'ServicePrincipal':
            credential_provider = RedisAsyncUtil.get_credential()
            client = Redis(host=redis_host, port=redis_port, credential_provider=credential_provider, ssl=True)
            return client
        return None

    @staticmethod
    def get_credential():
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        client_tenant_id = os.environ.get("AZURE_TENANT_ID")
        credential_provider = create_from_service_principal(client_id, client_secret, client_tenant_id)
        return credential_provider

    async def set(self, key, value, expiration=None):
        """Sets a value in the redis for the specified key"""
        value_to_store = value
        if value is None:
            value_to_store = ""
        value_to_store = value_to_store.encode('utf-8')
        await self.redis_client.set(key, value_to_store, ex=expiration)
        return self

    async def set_json(self, key, value, expiration=None):
        """Sets a value in the redis for the specified key after the item is JSON serialized"""
        value_to_serialize = json.dumps(value)
        return await self.set(key, value_to_serialize, expiration)

    async def get(self, key):
        """Gets a value from the redis for the specified key"""
        return_value = await self.redis_client.get(key)
        if return_value is None:
            return None
        else:
            return return_value.decode("utf-8")

    async def get_json(self, key: str):
        """Gets a deserialized value from the redis for the specified key"""
        serialized_value = await self.get(key)
        if serialized_value is None or serialized_value == "":
            serialized_value = '{}'
        de_serialized_value = json.loads(serialized_value)
        return de_serialized_value

    async def delete(self, key):
        """Deletes a value from the redis for the specified key"""
        await self.redis_client.delete(key)

    async def l_push(self, key, values):
        """Appends a value to the head of the list for the specified key to the head of the list"""
        await self.redis_client.lpush(key, values)
        return self

    async def l_range(self, key, start, end):
        """Retrieves the items in the list for the specified key"""
        return await self.redis_client.lrange(key, start, end)

    async def r_push(self, key, values):
        """Appends a value to the tail of the list for the specified key to the head of the list"""
        await self.redis_client.rpush(key, values)
        return self

    async def r_push_json(self, key, values):
        """Appends a value to the tail of the list for the specified key"""
        value_to_serialize = json.dumps(values)
        return await self.r_push(key, value_to_serialize)

    async def l_push_json(self, key, values):
        value_to_serialize = json.dumps(values)
        return await self.l_push(key, value_to_serialize)

    async def l_range_json(self, key, start, end):
        serialized_values = await self.l_range(key, start, end)
        deserialized_values: list = []
        for serialized_value in serialized_values:
            deserialized_value = json.loads(serialized_value)
            deserialized_values.append(deserialized_value)
        return deserialized_values

    async def l_range_all(self, key):
        return await self.l_range(key, 0, -1)

    async def l_range_json_all(self, key):
        return await self.l_range_json(key, 0, -1)

    async def increment(self, key, increment: int = 1) -> int:
        return await self.redis_client.incrby(key, increment)

    async def increment_float(self, key, increment: float = 1.0) -> float:
        return await self.redis_client.incrbyfloat(key, increment)

    async def decrement(self, key, decrement: int = 1):
        return await self.redis_client.decrby(key, decrement)

    async def decrement_float(self, key, decrement: float = 1.0):
        return await self.redis_client.incrbyfloat(key, (decrement * -1.0))

    async def exists(self, key):
        result = await self.redis_client.exists(key)
        if result:
            return True
        return False

    async def expire(self, key: str, time: int):
        return await self.redis_client.expire(key, time)

    async def set_expire(self, key, value, time: int):
        return await self.redis_client.setex(key, value, time)