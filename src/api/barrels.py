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
        if barrel_delivered.potion_type == [1,0,0,0]:
            num_red_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
        
        
    print(f"gold_paid: {gold_paid} num_red_ml: {num_red_ml} num_green_ml: {num_green_ml} num_dark_ml: {num_dark_ml}")

    gold_change = -1 * gold_paid

    with db.engine.begin() as connection:
        """
        connection.execute(
            sqlalchemy.text(
                "
                UPDATE global_inventory SET
                num_red_ml = num_red_ml + :num_red_ml,
                num_green_ml = num_green_ml + :num_green_ml,
                num_blue_ml = num_blue_ml + :num_blue_ml,
                num_dark_ml = num_dark_ml + :num_dark_ml,
                gold = gold - :gold_paid
                "),
                [{"num_red_ml": num_red_ml,"num_green_ml": num_green_ml,"num_blue_ml": num_blue_ml,"num_dark_ml": num_dark_ml,"gold_paid": gold_paid}])
        """

        gold_ledger_result = connection.execute(
            sqlalchemy.text("""
                            INSERT INTO gold_ledger (gold_change)
                            VALUES (:gold_change)
                            RETURNING id
                            """),
                           [{"gold_change": gold_change}]
        )

        # Retrieve the gold_ledger_id generated for the new row
        gold_ledger_id = gold_ledger_result.scalar()

        # Insert a new row into barrel_ledger and connect it with the gold_ledger_id
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO barrel_ledger (red_ml_change, green_ml_change, blue_ml_change, dark_ml_change, gold_ledger_id)
                            VALUES (:red_ml_change, :green_ml_change, :blue_ml_change, :dark_ml_change, :gold_ledger_id)
                            """),
                            {"red_ml_change": num_red_ml, "green_ml_change": num_green_ml, "blue_ml_change": num_blue_ml, "dark_ml_change": num_dark_ml, "gold_ledger_id": gold_ledger_id}
        )

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

    gold_sql_to_execute ="""
                        SELECT SUM(gold_change) as total_gold
                        FROM gold_ledger;
                        """

    ml_sql_to_execute ="""
                        SELECT SUM(red_ml_change) as total_red_ml, 
                            SUM(green_ml_change) as total_green_ml, 
                            SUM(blue_ml_change) as total_blue_ml, 
                            SUM(dark_ml_change) as total_dark_ml
                        FROM barrel_ledger;
                        """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(ml_sql_to_execute)).first()

        total_red_ml = result.total_red_ml
        total_green_ml = result.total_green_ml
        total_blue_ml = result.total_blue_ml
        total_dark_ml = result.total_dark_ml

        my_gold = connection.execute(sqlalchemy.text(gold_sql_to_execute)).scalar_one()
    
    barrel_dict = {}

    for barrel in wholesale_catalog:
        barrel_dict[barrel.sku] = 0
        # going to need to change the 1000 number 
        if barrel.potion_type == [0, 1, 0, 0]:
            if (my_gold > barrel.price) & (total_green_ml < 1000):
                #num_dark_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price
        if barrel.potion_type == [1, 0, 0, 0]:
            if (my_gold > barrel.price) & (total_red_ml < 1000):
                #num_blue_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price
        if barrel.potion_type == [0, 0, 1, 0]:
            if (my_gold > barrel.price) & (total_blue_ml < 1000):
                #num_blue_barrel_buy += 1
                barrel_dict[barrel.sku] += 1
                my_gold = my_gold - barrel.price
        if barrel.potion_type == [1, 0, 0, 0]:
            if (my_gold > barrel.price) & (total_dark_ml < 1000):
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

