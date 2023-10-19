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

    gold_paid = 0
    num_red_ml = 0 
    num_blue_ml = 0
    num_green_ml = 0 
    num_dark_ml = 0

    for barrel_delivered in barrels_delivered:
        gold_paid += barrel_delivered.price * barrel_delivered.quantity
        if barrel_delivered.potion_type == [0,0,0,1]:
            num_dark_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        if barrel_delivered.potion_type == [0,1,0,0]:
            num_green_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        if barrel_delivered.potion_type == [0,0,1,0]:
            num_blue_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        #if barrel_delivered.potion_type == [1,0,0,0]:
        #    num_red_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        
        
    print(f"gold_paid: {gold_paid} num_red_ml: {num_red_ml} num_green_ml: {num_green_ml} num_dark_ml: {num_dark_ml}")

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET
                num_red_ml = num_red_ml + :num_red_ml,
                num_green_ml = num_green_ml + :num_green_ml,
                num_blue_ml = num_blue_ml + :num_blue_ml,
                num_dark_ml = num_dark_ml + :num_dark_ml,
                gold = gold - :gold_paid
                """),
                [{"num_red_ml": num_red_ml,"num_green_ml": num_green_ml,"num_blue_ml": num_blue_ml,"num_dark_ml": num_dark_ml,"gold_paid": gold_paid}])

    return "OK"

    """
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

    """

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    sql_to_execute = "SELECT * FROM global_inventory"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()
    
    my_gold = result.gold
    barrel_dict = {}

    for barrel in wholesale_catalog:
        barrel_dict[barrel.sku] = 0
        # going to need to change the 1000 number 
        if barrel.potion_type == [0, 1, 0, 0]:
            if (my_gold > barrel.price) & (result.num_green_ml < 1000):
                #num_dark_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price
        if barrel.potion_type == [1, 0, 0, 0]:
            if (my_gold > barrel.price) & (result.num_red_ml < 1000):
                #num_blue_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price
        if barrel.potion_type == [0, 0, 1, 0]:
            if (my_gold > barrel.price) & (result.num_blue_ml < 1000):
                #num_blue_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price
        if barrel.potion_type == [1, 0, 0, 0]:
            if (my_gold > barrel.price) & (result.num_dark_ml < 1000):
                #num_dark_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price

    plan = []

    for key, value in barrel_dict.items():
            if value > 0:
                plan.append(
                    {
                        "sku": key,
                        "quantity": value,
                    })


    return plan

