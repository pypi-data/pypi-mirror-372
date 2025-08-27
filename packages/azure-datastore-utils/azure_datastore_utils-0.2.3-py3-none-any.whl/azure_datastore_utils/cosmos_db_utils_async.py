import os
from typing import Any, Dict, List, Union, Iterable

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, ContainerProxy, DatabaseProxy
from azure.cosmos.container import PartitionKeyType
from azure.identity import DefaultAzureCredential

from .cosmos_db_utils import CosmosDbAuthStrategy


class CosmosDBAsyncUtils:
    """Utility class for interacting with Azure Cosmos DB.

    This class abstracts away the complexities of authenticating, connecting,
    and performing CRUD (Create, Read, Update, Delete) operations on Cosmos DB
    containers (collections). It supports both connection string and
    managed identity authentication strategies.

    Attributes:
        client (CosmosClient): The Cosmos DB client instance.
        database_name (str): Name of the Cosmos DB database, loaded from environment.
        collection_name (str): Name of the Cosmos DB container (collection).
    """

    def __init__(self, collection: str, auth_strategy: CosmosDbAuthStrategy):
        """Initializes the CosmosDBUtils instance.

        Args:
            collection (str): The name of the collection (container) to interact with.
            auth_strategy (CosmosDbAuthStrategy): The authentication strategy to use.
                Must be either "ConnectionString" or "DefaultCredential".
        """
        self.client: CosmosClient = CosmosDBAsyncUtils.__prepare_client(auth_strategy)
        self.database_name: str = os.environ["COSMOS_DATABASE_NAME"]
        self.collection_name: str = collection

    @staticmethod
    def __prepare_client(auth_strategy: CosmosDbAuthStrategy) -> CosmosClient:
        """Prepares a CosmosClient instance based on the given authentication strategy.

        Args:
            auth_strategy (CosmosDbAuthStrategy): The authentication method to use.
                - "ConnectionString": Uses a Cosmos DB connection string from environment.
                - "DefaultCredential": Uses Azure Managed Identity (DefaultAzureCredential).

        Returns:
            CosmosClient: Configured Cosmos DB client.
        """
        if auth_strategy == 'ConnectionString':
            cosmos_connection_string = os.environ["COSMOS_CONNECTION_STRING"]
            return CosmosClient.from_connection_string(conn_str=cosmos_connection_string)
        elif auth_strategy == 'DefaultCredential':
            cosmos_endpoint = os.environ["COSMOS_ENDPOINT"]
            credential = DefaultAzureCredential()
            return CosmosClient(cosmos_endpoint, credential)

    async def create_collection(self, partition_key_path: str) -> ContainerProxy:
        """Creates a collection (container) in the database if it does not already exist.

        Args:
            partition_key_path (str): The partition key path for the container.

        Returns:
            ContainerProxy: The created or existing container proxy.
        """
        partition_key_path = PartitionKey(path=partition_key_path)
        return await self.get_database().create_container_if_not_exists(
            id=self.collection_name,
            partition_key=partition_key_path
        )

    def get_database(self) -> DatabaseProxy:
        """Gets a database proxy client for the configured database.

        Returns:
            DatabaseProxy: Proxy object to interact with the database.
        """
        return self.client.get_database_client(self.database_name)

    def get_collection(self) -> ContainerProxy:
        """Gets a container proxy client for the configured collection.

        Returns:
            ContainerProxy: Proxy object to interact with the collection.
        """
        return self.get_database().get_container_client(self.collection_name)

    def update_database_name(self, database_name: str):
        """Updates the current database name.

        Args:
            database_name (str): The new database name.

        Returns:
            CosmosDBUtils: The current instance, allowing method chaining.
        """
        self.database_name = database_name
        return self

    def update_collection_name(self, collection_name: str):
        """Updates the current collection (container) name.

        Args:
            collection_name (str): The new collection name.

        Returns:
            CosmosDBUtils: The current instance, allowing method chaining.
        """
        self.collection_name = collection_name
        return self

    async def get_single_item(self, item_id: str, partition_key: Any | None = None) -> Dict[str, Any]:
        """Retrieves a single item by ID.

        Args:
            item_id (str): The ID of the item to retrieve.
            partition_key (Any | None): The partition key value of the item. Defaults to None.

        Returns:
            dict: The retrieved item as a dictionary.
        """
        container_proxy = self.get_collection()
        return await container_proxy.read_item(item=item_id, partition_key=partition_key)

    async def get_all_items(self, max_item_count: int | None = None) -> List[Dict[str, Any]]:
        """Retrieves all items from the collection.

        Args:
            max_item_count (int | None): The maximum number of items to return. Defaults to None.

        Returns:
            list[dict]: A list of items in the collection.
        """
        container_proxy = self.get_collection()
        all_items = await container_proxy.read_all_items(max_item_count=max_item_count)
        return [item for item in all_items]

    async def create_item(self, item: dict) -> Dict[str, Any]:
        """Creates a new item in the collection.

        Args:
            item (dict): The item to create.

        Returns:
            dict: The created item as returned by Cosmos DB.
        """
        container_proxy = self.get_collection()
        return await container_proxy.create_item(item)

    async def upsert_item(self, item: dict) -> Dict[str, Any]:
        """Creates or updates (upserts) an item in the collection.

        Args:
            item (dict): The item to create or update.

        Returns:
            dict: The upserted item as returned by Cosmos DB.
        """
        container_proxy = self.get_collection()
        return await container_proxy.upsert_item(item)

    async def patch_item(
        self,
        item: Union[str, Dict[str, Any]],
        partition_key: PartitionKeyType,
        patch_operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Partially updates (patches) an item with the specified patch operations.

        Supported operations:
            - add: Adds a new property or appends to an array (fails if property exists).
            - replace: Replaces the value of an existing property (fails if not exists).
            - remove: Removes an existing property.
            - set: Adds or replaces the value of a property.
            - incr: Increments a numeric property by a specified value.

        Args:
            item (str | dict): Item ID or full item dictionary (must include 'id').
            partition_key (Any): Partition key of the item.
            patch_operations (list[dict]): List of patch operations. Each operation should
                include "op", "path", and optionally "value".

        Returns:
            dict: The updated item after patch.
        """
        container_proxy = self.get_collection()
        return await container_proxy.patch_item(item, partition_key=partition_key, patch_operations=patch_operations)

    async def delete_item(self, item: dict[str, Any] | str, partition_key: Any) -> Dict[str, Any]:
        """Deletes an item from the collection.

        Args:
            item (dict | str): The item or item ID to delete.
            partition_key (Any): The partition key value for the item.

        Returns:
            dict: The response from the delete operation.
        """
        container_proxy = self.get_collection()
        return await container_proxy.delete_item(item, partition_key=partition_key)

    async def query_container(
        self,
        query: str,
        parameters: list[dict[str, object]] | None = None,
        partition_key: Any | None = None,
        enable_cross_partition_query: bool | None = None,
        max_item_count: int | None = None
    ) -> Iterable[Dict[str, Any]]:
        """Executes a SQL query against the container.

        Args:
            query (str): The SQL query string to execute.
            parameters (list[dict] | None): Query parameters. Defaults to None.
            partition_key (Any | None): Partition key to filter results. Defaults to None.
            enable_cross_partition_query (bool | None): Whether to enable cross-partition queries. Defaults to None.
            max_item_count (int | None): Maximum number of items to return. Defaults to None.

        Returns:
            Iterable[dict]: Query results as an iterable of items.
        """
        container_proxy = self.get_collection()
        return await container_proxy.query_items(
            query,
            parameters=parameters,
            partition_key=partition_key,
            enable_cross_partition_query=enable_cross_partition_query,
            max_item_count=max_item_count
        )
