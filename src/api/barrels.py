from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    for barrel in barrels_delivered:
        with db.engine.begin() as connection:
            if barrel.potion_type == [1, 0, 0, 0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + " + str(barrel.ml_per_barrel)))
            elif barrel.potion_type == [0, 1, 0, 0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + " + str(barrel.ml_per_barrel)))
            elif barrel.potion_type == [0, 0, 1, 0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + " + str(barrel.ml_per_barrel)))
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - " + str(barrel.price)))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    sql_to_execute = "SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()
    
    my_gold = result.gold

    num_red_barrel_buy = 0
    num_green_barrel_buy = 0
    num_blue_barrel_buy = 0
    for barrel in wholesale_catalog:
        if barrel.potion_type == [0, 0, 1, 0]:
            if (my_gold > barrel.price) & (result.num_blue_potions < 2):
                num_blue_barrel_buy += 1
                my_gold = my_gold - barrel.price
        elif barrel.potion_type == [0, 1, 0, 0]:
            if (my_gold > barrel.price) & (result.num_green_potions < 5):
                num_blue_barrel_buy += 1
                my_gold = my_gold - barrel.price
        elif barrel.potion_type == [1, 0, 0, 0]:
            if (my_gold > barrel.price) & (result.num_red_potions < 10):
                num_red_barrel_buy += 1
                my_gold = my_gold - barrel.price

    plan = []

    if num_red_barrel_buy > 0:
        plan.append(
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": num_red_barrel_buy,
            })
    if num_green_barrel_buy > 0:
        plan.append({
                "sku": "SMALL_GREEN_BARREL",
                "quantity": num_green_barrel_buy,
            })
    if num_blue_barrel_buy > 0:
        plan.append({
                "sku": "SMALL_BLUE_BARREL",
                "quantity": num_blue_barrel_buy,
            })

    return plan

