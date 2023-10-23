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

    potions_sql_to_execute="""
                            SELECT SUM(red_potions) as total_red, 
                                SUM(green_potions) as total_green, 
                                SUM(blue_potions) as total_blue, 
                                SUM(dark_potions) as total_dark,
                                SUM(christmas_potions) as total_christmas, 
                                SUM(purple_potions) as total_purple, 
                                SUM(cyan_potions) as total_cyan
                            FROM potions_ledger;
                            """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(ml_sql_to_execute)).first()

        total_ml = result.total_dark_ml + result.total_blue_ml + result.total_green_ml + result.total_red_ml

        my_gold = connection.execute(sqlalchemy.text(gold_sql_to_execute)).scalar_one()

        result_potions = connection.execute(sqlalchemy.text(potions_sql_to_execute)).first()

        total_potions = result_potions.total_red + result_potions.total_green + result_potions.total_blue + result_potions.total_dark + result_potions.total_christmas + result_potions.total_purple + result_potions.total_cyan


    return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": my_gold}


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
