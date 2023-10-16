from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """

    sql_to_execute = "SELECT * FROM global_inventory"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()
        total_potions = connection.execute(
                            sqlalchemy.text("""
                                            SELECT SUM(inventory) AS total_quantity
                                            FROM potions"""
                                            ))

    ml_in_barrles = result.num_red_ml + result.num_blue_ml + result.num_green_ml + result.num_dark_ml
    gold = result.gold


    return {"number_of_potions": total_potions, "ml_in_barrels": ml_in_barrles, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
