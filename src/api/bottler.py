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

    sql_to_execute = "SELECT * FROM global_inventory;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))

    first_row = result.first()


    num_bottles = first_row.num_red_ml // 100 

    new_bottles = first_row.num_red_potions + num_bottles
    new_ml = first_row.num_red_ml - (num_bottles * 100)

    sql_to_execute = "UPDATE global_inventory SET num_red_potions = {new_bottles}, num_red_ml = {new_ml} WHERE id = 1;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_bottles,
            }
        ]
