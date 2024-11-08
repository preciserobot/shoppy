import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

ITEM_PREFIX = "item:"

DATA_SOURCES = [
    (
        lambda ean: f'https://opengtindb.org/?ean={ean}&cmd=query&queryid=400000000',
        {
            'name': 'info.name',
            'detail': 'info.description',
            'quantity': 'info.quantity',
            'unit': 'info.unit',
            '_data': 'info',
        }
    ),
    (
        lambda ean: f'https://world.openfoodfacts.org/api/v0/product/{ean}.json',
        {
            'name': 'product.product_name',
            'detail': 'product.ingredients_text',
            'quantity': 'product.quantity',
            'unit': 'product.quantity_unit',
            '_data': 'product',
        }
    ),
]