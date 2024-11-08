import pytest
import json
from bs4 import BeautifulSoup
from app.main import app
from fastapi.testclient import TestClient
from app.models import Item


client = TestClient(app)

# FORM create item
def test_create_product_form(items):
    for item in items:
        response = client.post("/items", data=item)
        assert response.status_code == 200, f"Error while creating product {response.text})"
        # validate html response
        assert response.headers['content-type'] == 'text/html; charset=utf-8', f"Error while creating product {response.text})"

# API get item
def test_get_product(barcodes):
    '''get/add a product and check if it is there'''
    for ean, status_code in barcodes:
        create = status_code == 201
        response = client.get(f"/items/{ean}?create={create}")
        assert response.status_code == status_code, f"Error while fetching product {ean} {response.text})"
        # validate data
        if status_code in [200, 201]:
            data = response.json()
            Item(**data)

# API get items
def test_get_all_products_json(barcodes):
    '''get all products and check if they are there'''
    response = client.get(f"/items", headers={'content-type': 'application/json'})
    assert response.status_code == 200, f"Error while fetching products {response.text})"
    data = response.json()
    # check if all expected products are there (200)
    expected_products = [ean for ean, status_code in barcodes if status_code <= 202]
    fetched_products = [item['ean'] for item in data]
    assert set(expected_products) <= set(fetched_products), f"Error while fetching products {response.text})"
    # validate data
    for item in data:
        Item(**item)

# WEB get items
def test_get_all_product_html(barcodes):
    '''get all products and check if they are there'''
    response = client.get(f"/items")
    assert response.status_code == 200, f"Error while fetching products {response.text})"
    # parse html
    soup = BeautifulSoup(response.text, 'html.parser') 
    li_items = soup.find('ul', {'id': 'items'}).find_all('li')  # Find the <ul> element with id 'items'
    assert len(li_items) > 0, f"Error while fetching products {response.text})"
    # check if all expected products are there (20X)
    expected_products = [ean for ean, status_code in barcodes if status_code <= 202]
    fetched_products = [ li.find('form').find('input', {'name': 'ean'}).get('value') \
        for li in li_items ]
    assert set(expected_products) <= set(fetched_products), f"Error while fetching products {response.text})"

# API update item
def test_update_product_json(barcodes, random_food):
    '''change a field and check if it has changed'''
    for ean in [ b for b, s in barcodes if s < 202 ]:
        new_name = random_food()
        response = client.put(f"/items", json={"ean": ean, "name": new_name})
        assert response.status_code == 200, f"Error while updating product {response.text})"
        # validate data
        data = response.json()
        item = Item(**data)
        # check if name has been updated
        assert item.name == new_name, f"Error while updating product {response.text})"

# FORM update item
def test_update_product_form(barcodes, random_food):
    '''change a field and check if it has changed'''
    for ean in [ b for b, s in barcodes if s < 202 ]:
        new_name = random_food()
        response = client.post(f"/items/{ean}/update", data={"name": new_name})
        assert response.status_code == 200, f"Error while updating product {response.text})"
        # fetch changed item
        response = client.get(f"/items/{ean}")
        assert response.status_code == 200, f"Error while fetching product {ean} {response.text})"
        # validate changed field
        data = response.json()
        item = Item(**data)
        assert item.name == new_name, f"Error while updating product {response.text})"

# FORM delete item
def test_delete_product(barcodes):
    '''delete a product and check if it is gone'''
    for ean in [ b for b, s in barcodes if s == 200 ]:
        response = client.post(f"/items/{ean}/delete")
        assert response.status_code == 200, f"Error while deleting product {response.text})"
        # check if absent
        soup = BeautifulSoup(response.text, 'html.parser') 
        li_items = soup.find('ul', {'id': 'items'}).find_all('li')
        fetched_products = [ li.find('form').find('input', {'name': 'ean'}).get('value') \
            for li in li_items ]
        assert ean not in fetched_products, f"Error while deleting product {response.text})"
