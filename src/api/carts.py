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

    # new cart into table with "new_cart.customer" as customer

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
                                           INSERT INTO carts (customer)
                                           VALUES (:customer);
                                           """),
                                           [{"customer": new_cart.customer}]
        )


        return "OK"

        """
        sql_to_execute = "SELECT * FROM carts;"
        result = connection.execute(sqlalchemy.text(sql_to_execute)).first()

        cart = {"cart_id": str(result.id)}

        sql_to_execute = "SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory;"
        cartid = len(carts) + 1  # Generate a unique cart id based on the length of the list
        cart_data = {"cart_id": cartid, "customer": new_cart.customer}
        carts.append(cart_data)
        return cart_data

        """

# this one needs to change
@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    # return a cart with all the stuff 

    return carts[cart_id - 1]
    #return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    with db.engine.begin() as connection:
    # set the cart_item quantity to to whetver, set cart_id to whatever, set item_sku to whaterver 
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO cart_items (sku, cart_id, quantity, potion_id)
                            SELECT :sku, :cart_id, :quantity, p.id
                            FROM potions p
                            WHERE p.sku = :sku;
                            """),
                            {"sku": item_sku, "cart_id": cart_id, "quantity": cart_item.quantity}
        )

    return "OK"

    """
            connection.execute(
                    sqlalchemy.text(" 
                                    UPDATE cart_items SET 
                                    quantity = quantity + :quantity,
                                    cart_id = :cart_id
                                    WHERE sku = :sku
                                    "),
                    [{"quantity": cart_item.quantity,
                    "cart_id": cart_id,
                    "sku": item_sku}]
                )
    """

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    
    with db.engine.begin() as connection:
        total_potions = connection.execute(
            sqlalchemy.text("""
                            SELECT SUM(quantity) AS total_potions
                            FROM cart_items
                            JOIN potions ON potions.id = cart_items.potion_id
                            WHERE cart_id = :cart_id
                            """),
                            [{"cart_id": cart_id}]).scalar_one()


        total_gold = connection.execute(
            sqlalchemy.text("""
                            SELECT SUM(quantity*price) AS total_gold
                            FROM cart_items
                            JOIN potions ON potions.id = cart_items.potion_id
                            WHERE cart_id = :cart_id"""),
                            [{"cart_id": cart_id}]).scalar_one()

        connection.execute(
            sqlalchemy.text("""
                            UPDATE potions
                            SET inventory = inbentoru - cart_items.quantity 
                            WHERE potions.id = cart_items.potion_id and cart_items.cart_id = :cart_id
                            UPDATE globals
                            SET gold = gold + :total_gold
                            """), [{"total_gold": total_gold}])

    return {"total_potions_bought": total_potions, "total_gold_paid": total_gold}




"""
    cart_index = cart_id - 1


    # given cart_id, total up all the potions, and gold in the cart 
    # update, potions db and global inventories with the new gold 

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
    
    item_prices = {"RED_POTION_0": 50, "GREEN_POTION_0": 60, "BLUE_POTION_0": 70}
    return item_prices.get(item_sku, None)

"""