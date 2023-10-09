from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    for potion in potions_delivered:
        if potion.potion_type == [100, 0, 0, 0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - " + str(potion.quantity * 100)))
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + " + str(potion.quantity)))
        if potion.potion_type == [0, 100, 0, 0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - " + str(potion.quantity * 100)))
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + " + str(potion.quantity)))
        if potion.potion_type == [0, 0, 100, 0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - " + str(potion.quantity * 100)))
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + " + str(potion.quantity)))
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    sql_to_execute = "SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()

    num_red_bottles = result.num_red_ml // 100 
    num_green_bottles = result.num_green_ml // 100
    num_blue_bottles = result.num_blue_ml // 100

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_red_bottles,
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": num_green_bottles,
            },
                        {
                "potion_type": [0, 0, 100, 0],
                "quantity": num_blue_bottles,
            }
        ]
