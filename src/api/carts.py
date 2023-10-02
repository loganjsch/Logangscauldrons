from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

carts = []
cartid = 0

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    global cartid
    cartid += 1
    carts[cartid] = {}
    return cartid
    #return {"cart_id": cartid}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return carts[cartid]
    #return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    carts[cartid][item_sku] = cart_item.quantity
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    total_potions_bought = 0
    for item_val in carts[cartid].values():
        total_potions_bought += item_val

    total_gold_paid = 50 * total_potions_bought
    # sql goes here 

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions - " + str(total_potions_bought)))
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + " + str(total_gold_paid)))

    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
