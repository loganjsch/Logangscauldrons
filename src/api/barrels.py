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

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    sql_to_execute = "SELECT * FROM global_inventory;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    
    first_row = result.first()
    my_gold = first_row.gold

    num_barrel_buy = 3
    num_ml_add = 0
    for barrel in wholesale_catalog:
        for _ in range(barrel.quantity):
            if (my_gold > barrel.price) & (first_row.num_red_potion < 10):
                num_barrel_buy += 1
                num_ml_add += barrel.ml_per_barrel
                my_gold = my_gold - barrel.price

    new_num_ml = first_row.num_red_ml + num_ml_add

    
    #sql_to_execute = "UPDATE global_inventory SET num_red_ml = {new_num_ml}, gold = {my_gold} WHERE id = 1;"

    #with db.engine.begin() as connection:
    #    connection.execute(sqlalchemy.text(sql_to_execute))

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": num_barrel_buy,
        }
    ]
