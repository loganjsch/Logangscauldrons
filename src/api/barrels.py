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

    '''
    num_barrel_buy = 0
    my_gold = 100
    for barrel in wholesale_catalog:
        if my_gold > barrel.price:
            if first_row.num_red_potion < 10):
                num_barrel_buy += 1
                my_gold = my_gold - barrel.price
    
    # now set my gold to my gold 
    # and set num of ml to barrel * ml_per_barrel
            

    sql_to_execute = "SELECT num_red_potions FROM global_inventory;"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    first_row = result.first()

    num_barrel_buy = gold // 100
    '''
    # reduce gold by num_barrel_by * 100
    # increase num_ml by num_barrel_by * ml per barrel

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]
