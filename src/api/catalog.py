from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    sql_to_execute = "SELECT num_red_potions FROM global_inventory;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()

    """
    if first_row.num_red_potions == 0:
        return [
            {}
        ]
    """

    return [
        {
            "sku": "RED_POTION_0",
            "name": "red potion",
            "quantity": result.num_red_potions,
            "price": 50,
            "potion_type": [100, 0, 0, 0],
        }
    ]


