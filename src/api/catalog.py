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

    sql_to_execute ="""
                    SELECT SUM(green_potions) as green_potions, 
                        SUM(purple_potions) as purple_potions, 
                        SUM(christmas_potions) as christmas_potions, 
                        SUM(blue_potions) as blue_potions, 
                        SUM(red_potions) as red_potions, 
                        SUM(cyan_potions) as cyan_potions,
                        SUM(dark_potions) as dark_potions
                    FROM potions_ledger;
                    """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()

        potions_dict = {}

        potions_dict["green_potion_0"] = result.green_potions
        potions_dict["red_potion_0"] = result.red_potions
        potions_dict["blue_potion_0"] = result.blue_potions
        potions_dict["dark_potion_0"] = result.dark_potions
        potions_dict["purple_potion_0"] = result.purple_potions
        potions_dict["christmas_potion"] = result.christmas_potions
        potions_dict["cyan_potion"] = result.cyan_potions

        catalog = []
        for key, value in potions_dict.items():
            if value > 0:
                potion_res = connection.execute(sqlalchemy.text("""
                                                SELECT FROM potions WHERE sku = :sku
                                                """), {"sku": key,}).first()
                catalog.append(
                    {
                    "sku": key,
                    "name": key,
                    "quantity": value,
                    "price": potion_res.cost,
                    "potion_type": potion_res.potion_type,
                })

        return catalog

    """

    if result.num_red_potions > 0:
        catalog.append(
            {
            "sku": "RED_POTION_0",
            "name": "red potion",
            "quantity": result.num_red_potions,
            "price": 50,
            "potion_type": [100, 0, 0, 0],
        })
    if result.num_green_potions > 0:
        catalog.append(
        {
            "sku": "GREEN_POTION_0",
            "name": "green potion",
            "quantity": result.num_green_potions,
            "price": 60,
            "potion_type": [0, 100, 0, 0],
        })
    if result.num_blue_potions > 0:
        catalog.append(
        {
            "sku": "BLUE_POTION_0",
            "name": "blue potion",
            "quantity": result.num_blue_potions,
            "price": 70,
            "potion_type": [0, 0, 100, 0],
        })

    return catalog

    """
