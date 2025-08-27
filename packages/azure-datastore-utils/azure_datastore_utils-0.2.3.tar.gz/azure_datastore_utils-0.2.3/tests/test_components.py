
import asyncio
from typing import Any, Dict

from azure_datastore_utils import AsyncSearchClientDao, SearchClientDao, CosmosDBUtils, RedisUtil
from pydantic import BaseModel


class Replenishment(BaseModel):
    id: str
    replenishment_id: str
    transaction_date: str
    sku_id: str
    units: float
    vendor_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Replenishment":
        """
        Create a Replenishment object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing replenishment attributes.

        Returns:
            Replenishment: A validated Replenishment instance.
        """
        return cls.model_validate(data)

async def search_product_inventory():
    client = AsyncSearchClientDao('product_inventory', auth_strategy='Password')
    document_count = await client.get_document_count()
    print(document_count)
    await client.close()

async def search_net_sales():
    client = AsyncSearchClientDao('net_sales', auth_strategy='Password')
    document_count = await client.get_document_count()
    print(document_count)
    await client.close()

async def query_documents():
    client = SearchClientDao('product_inventory', auth_strategy='Password')
    results = client.query_index("*", query_filter="department eq 'appliance'")
    print(results)

async def query_collection():
    client = SearchClientDao('product_inventory', auth_strategy='Password')
    results = client.query_index("*", query_filter="sku_id eq '101'")
    print(results)

async def get_all_docs():
    client = CosmosDBUtils(database_name="retailstore", collection="replenishments", auth_strategy='ConnectionString')

    all_items = client.get_all_items()
    print(all_items)

    single_item = client.get_single_item(item_id='3000', partition_key='30001')
    print(single_item)

async def create_item():
    client = CosmosDBUtils(database_name="retailstore", collection="replenishments", auth_strategy='ConnectionString')
    item = Replenishment(
        id="sku123",
        replenishment_id="repl-2025-01",
        transaction_date="2025-08-22T10:30:00",
        sku_id="sku123",
        units=50,
        vendor_id="vendor456"
    )

    client.create_item(item.model_dump())

async def fetch_item():
    client = CosmosDBUtils(database_name="retailstore", collection="replenishments", auth_strategy='ConnectionString')

    item = client.get_single_item(item_id='sku123', partition_key='vendor456')

    item2 = Replenishment.from_dict(item)

    print(item2)


async def cart_id():

    client = RedisUtil(auth_strategy='Password')

    cart_identifier = client.increment("cart_id")

    print(cart_identifier)

async def save_cart():
    client = RedisUtil(auth_strategy='Password')
    item = Replenishment(
        id="sku123",
        replenishment_id="repl-2025-01",
        transaction_date="2025-08-22T10:30:00",
        sku_id="sku123",
        units=50,
        vendor_id="vendor456"
    )

    key = 'cart_contents'
    client.set_json(key, item.model_dump())

async def fetch_cart():
    key = 'cart_contents'
    client = RedisUtil(auth_strategy='Password')
    cart_contents = client.get_json(key)
    print(cart_contents)

async def main():
    print("Running tests ...")
    await fetch_cart()
    await query_documents()

if __name__ == '__main__':
    asyncio.run(main())
