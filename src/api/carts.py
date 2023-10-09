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

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    cartid = len(carts) + 1  # Generate a unique cart id based on the length of the list
    cart_data = {"cart_id": cartid, "customer": new_cart.customer}
    carts.append(cart_data)
    return cart_data


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return carts[cart_id - 1]
    #return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    carts[cart_id - 1][item_sku] = cart_item.quantity
    return str(carts[cart_id - 1][item_sku])


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    cart_index = cart_id - 1

    if cart_index < 0 or cart_index >= len(carts):
        return {"error": "Cart not found"}

    cart = carts[cart_index]
    total_potions_bought = 0
    red_potions_bought = 0
    blue_potions_bought = 0
    green_potions_bought = 0
    total_gold_paid = 0

    for item_sku, quantity in cart.items():
        item_price = get_item_price(item_sku)

        if item_sku == "RED_POTION_0":
            red_potions_bought += quantity
            total_gold_paid += item_price * quantity
        elif item_sku == "GREEN_POTION_0":
            green_potions_bought += quantity
            total_gold_paid += item_price * quantity
        elif item_sku == "BLUE_POTION_0":
            blue_potions_bought += quantity
            total_gold_paid += item_price * quantity

    # Now you have the total_potions_bought and total_gold_paid for the cart

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions - " + str(red_potions_bought)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions - " + str(green_potions_bought)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions - " + str(blue_potions_bought)))
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + " + str(total_gold_paid)))

    total_potions_bought = red_potions_bought + blue_potions_bought + green_potions_bought

    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}


def get_item_price(item_sku):
    
    item_prices = {"RED_POTION_0": 50, "GREEN_POTION_0": 75, "BLUE_POTION_0": 100}
    return item_prices.get(item_sku, None)