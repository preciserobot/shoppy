import pytest
import random

@pytest.fixture(scope="session")
def barcodes():
    return [
        ("5000436508298", 200),  # tesco semi skimmed 2l
        ("5051399182506", 200),  # tesco chickpeas in water 400g (or garlic bread?)
        ("1234567891011", 201),  # unknown item (created)
        ("1234567891012", 404),  # non
    ]

@pytest.fixture(scope="session")
def items():
    return [
        {
            "ean": "5000436508298",
            "name": "Tesco Semi Skimmed Milk 2L",
            "detail": "2 litres of semi skimmed milk",
            "quantity": "1",
            "unit": "bottle",
        },
        {
            "ean": "5051399182506",
            "name": "Tesco Chickpeas in Water 400g",
            "detail": "400g of chickpeas in water",
            "quantity": "1",
            "unit": "tin",
        },
    ]

@pytest.fixture(scope="function")
def random_food():
    foods = [
        "Bread",
        "Milk",
        "Cheese",
        "Butter",
        "Eggs",
        "Chicken",
        "Beef",
        "Pork",
        "Fish",
        "Apples",
        "Bananas",
        "Oranges",
        "Grapes",
        "Strawberries",
        "Raspberries",
        "Blueberries",
        "Blackberries",
        "Tomatoes",
        "Cucumbers",
        "Carrots",
        "Potatoes",
        "Onions",
        "Garlic",
    ]
    # return arbitrary item from list
    return lambda: random.choice(foods)
    