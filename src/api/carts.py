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
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    """
    total_potions_bought = 0
    for item_val in carts[cart_id - 1].values():
        total_potions_bought += int(item_val)
    """
    cart_index = cart_id - 1

    if cart_index < 0 or cart_index >= len(carts):
        return {"error": "Cart not found"}

    cart = carts[cart_index]
    total_potions_bought = 0
    total_gold_paid = 0

    for item_sku, quantity in cart.items():
        # You may need to define a mapping from item_sku to item price
        # For example, if item_sku is the SKU of the item, you can fetch its price from a database or a predefined dictionary.
        # Assuming item_price is a placeholder for the item's price:
        item_price = get_item_price(item_sku)

        if item_price is not None:
            total_potions_bought += quantity
            total_gold_paid += item_price * quantity

    # Now you have the total_potions_bought and total_gold_paid for the cart
    # You can perform further actions such as updating the database here.

    

    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}

    total_gold_paid = 50 * total_potions_bought
    # sql goes here 

    '''
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions - " + str(total_potions_bought)))
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + " + str(total_gold_paid)))

    '''

    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}

def get_item_price(item_sku):
    # Replace this with your logic to fetch the item's price from a database or a dictionary
    # Example:
    item_prices = {"small_red_potion": 50, "item_sku_2": 15, "item_sku_3": 20}
    return item_prices.get(item_sku, None)