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
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red _ml + " + str(barrel.ml_per_barrel)))
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - " + str(barrel.price)))
        return "OK"
    

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

    num_barrel_buy = 0
    for barrel in wholesale_catalog:
        for _ in range(barrel.quantity):
            if (my_gold > barrel.price) & (first_row.num_red_potion < 10):
                num_barrel_buy += 1
                my_gold = my_gold - barrel.price

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": num_barrel_buy,
        }
    ]
