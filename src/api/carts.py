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
        id = connection.execute(sqlalchemy.text("""
                                           INSERT INTO carts (customer)
                                           VALUES (:customer)
                                           RETURNING id;
                                           """),
                                           [{"customer": new_cart.customer}]
        ).scalar_one()
    
        return {"cart_id": id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    # honestly idk what this is supposed to do

    return {}


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

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    total_potions = 0
    num_red_potions = 0
    num_green_potions = 0
    num_blue_potions = 0
    num_dark_potions = 0
    num_purple_potions = 0
    num_christmas_potions = 0
    num_cyan_potions = 0
    
    with db.engine.begin() as connection:
        cart = connection.execute(
            sqlalchemy.text("""
                            SELECT *
                            FROM cart_items
                            JOIN potions ON potions.id = cart_items.potion_id
                            WHERE cart_id = :cart_id
                            """),
                            [{"cart_id": cart_id}])


        total_gold = connection.execute(
            sqlalchemy.text("""
                            SELECT SUM(quantity*cost) AS total_gold
                            FROM cart_items
                            JOIN potions ON potions.id = cart_items.potion_id
                            WHERE cart_id = :cart_id
                            """),
                            [{"cart_id": cart_id}]).scalar_one()

        for cart_item in cart:
            match cart_item.potion_id:
                case 1:
                    num_christmas_potions -= cart_item.quantity
                case 2:
                    num_red_potions -= cart_item.quantity
                case 3:
                    num_blue_potions -= cart_item.quantity
                case 4:
                    num_dark_potions -= cart_item.quantity
                case 5:
                    num_green_potions -= cart_item.quantity
                case 6:
                    num_purple_potions -= cart_item.quantity
                case 7:
                    num_cyan_potions -= cart_item.quantity

        total_potions = num_red_potions + num_christmas_potions + num_cyan_potions + num_purple_potions + num_green_potions + num_blue_potions + num_dark_potions

        potion_ledger = connection.execute(
                sqlalchemy.text("""
                                INSERT INTO potions_ledger (red_potions, green_potions, blue_potions, dark_potions, purple_potions, christmas_potions, cyan_potions)
                                VALUES (:red_potions,:green_potions,:blue_potions,:dark_potions,:purple_potions,:christmas_potions,:cyan_potions)
                                RETURNING id
                                """),
                                {"red_potions": num_red_potions,"green_potions": num_green_potions,"blue_potions": num_blue_potions,"dark_potions": num_dark_potions,"purple_potions": num_purple_potions,"christmas_potions": num_christmas_potions,"cyan_potions": num_cyan_potions}
            ).scalar_one()
        
        connection.execute(
            sqlalchemy.text("""
                            INSERT INTO gold_ledger (gold_change, potions_ledger_id)
                            VALUES (:gold_change, :potions_ledger_id)
                            """),
                           [{"gold_change": total_gold, "potions_ledger_id": potion_ledger}]
        )

        return {"total_potions_bought": total_potions, "total_gold_paid": total_gold}

        """
        connection.execute(
            sqlalchemy.text("
                            UPDATE potions
                            SET inventory = inventory - cart_items.quantity 
                            FROM cart_items
                            WHERE potions.id = cart_items.potion_id and cart_items.cart_id = :cart_id;

                            UPDATE global_inventory
                            SET gold = gold + :total_gold
                            "), [{"total_gold": total_gold, "cart_id": cart_id}])
        """






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