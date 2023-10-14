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
    with db.engine.begin() as connection:
        print(potions_delivered)

        additional_potions = sum(potion.quantity for potion in potions_delivered)
        num_red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        num_green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        num_blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        num_dark_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)

        for potion_delivered in potions_delivered:
            connection.execute(
                sqlalchemy.text(""" 
                                UPDATE potions
                                SET inventory = inventory + :additional_potions
                                WHERE potion_type = :potion_type
                                """),
                [{"additonal_potions": potion_delivered.quantity,
                  "potion_type": potion_delivered.potion_type}]
            )
        
        connection.execute(
            sqlalchemy.text("""
                            UPDATE global_inventory SET
                            num_red_ml = num_red_ml - :num_red_ml,
                            num_green_ml = num_green_ml - :num_green_ml,
                            num_blue_ml = num_blue_ml - :num_blue_ml,
                            num_dark_ml = num_dark_ml - :num_dark_ml
                            """),
            [{"num_red_ml": num_red_ml, "num_green_ml": num_green_ml, "num_blue_ml": num_blue_ml, "num_dark_ml": num_dark_ml}]
        )

        return "OK"

        """
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

        """
        
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

    sql_to_execute = "SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()

        num_red_ml = result.num_red_ml
        num_green_ml = result.num_green_ml
        num_blue_ml = result.num_blue_ml
        num_dark_ml = result.num_dark_ml

        potions = connection.execute(sqlalchemy.text("SELECT * from potions ORDER BY id ASC"))

        plan = []

        ## i do not know what the logic should be here

        # dictionary to keep track of how many of each potion for the plan
        potion_dic = {}

        # This basically says go through the id order, and buy as much until i cant afford it anymore 
        # or there's 5 of this type (the 5 should be changed but its just to stop christmas
        # taking all the red and green for example)
        for row in potions:
            type_tuple = tuple(row.potion_type)
            potion_dic[type_tuple] = 0
            while ((num_red_ml >= row.potion_type[0]) and (num_green_ml >= row.potion_type[1]) 
            and (num_blue_ml >= row.potion_type[2]) and (num_dark_ml >= row.potion_type[3]) 
            and ((row.inventory + potion_dic[type_tuple]) < 6)):
                potion_dic[type_tuple] += 1

                # keep local counts up to date
                num_red_ml = num_red_ml - row.potion_type[0]
                num_green_ml = num_green_ml - row.potion_type[1]
                num_blue_ml = num_blue_ml - row.potion_type[2]
                num_dark_ml = num_dark_ml - row.potion_type[3]

        for key, value in potion_dic.items():
            if value > 0:
                plan.append(
                    {
                        "potion_type": list(key),
                        "quantity": value,
                    })

        return plan


    """

    num_red_bottles = result.num_red_ml // 100 
    num_green_bottles = result.num_green_ml // 100
    num_blue_bottles = result.num_blue_ml // 100


    if num_red_bottles > 0:
        plan.append(
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_red_bottles,
            })
    if num_green_bottles > 0:
        plan.append({
                "potion_type": [0, 100, 0, 0],
                "quantity": num_green_bottles,
            })
    if num_blue_bottles > 0:
        plan.append({
                "potion_type": [0, 0, 100, 0],
                "quantity": num_blue_bottles,
            })

    return plan

    """