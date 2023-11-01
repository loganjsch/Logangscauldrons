from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum
from sqlalchemy import *


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    metadata_obj = sqlalchemy.MetaData()
    potions = sqlalchemy.Table("potions", metadata_obj, autoload_with=db.engine)
    carts = sqlalchemy.Table("carts", metadata_obj, autoload_with=db.engine)
    cart_items = sqlalchemy.Table("cart_items", metadata_obj, autoload_with=db.engine)

    with db.engine.begin() as connection:
        # Build the query
        stmt = select([
            cart_items.c.id,
            cart_items.c.sku,
            carts.c.customer,
            cart_items.c.quantity,
            potions.c.cost,
            cart_items.c.created_at
        ]).join(carts, cart_items.c.cart_id == carts.c.id).join(potions, cart_items.c.potion_id == potions.c.id)

        if customer_name and potion_sku:
            stmt = stmt.where(and_(
                carts.c.customer == customer_name,
                potions.c.sku == potion_sku
            ))
        else:
            stmt = stmt.where(or_(
                carts.c.customer == customer_name,
                potions.c.sku == potion_sku
            ))

        # stmt = stmt.order_by(sort_col.asc()) if sort_order == "asc" else stmt.order_by(sort_col.desc())

        # Execute the query
        orders = connection.execute(stmt)

        result = []  # Initialize an empty list to store the results

        for row in orders:
            # Calculate line_item_total as cost * quantity
            line_item_total = row.cost * row.quantity

            # Create a dictionary for each row
            result_dict = {
                "line_item_id": row.id,
                "item_sku": row.sku,
                "customer_name": row.customer,
                "line_item_total": line_item_total,
                "timestamp": str(row.created_at),  # Convert timestamp to a string if needed
            }
            result.append(result_dict)  # Append the result to the list

        # Now, 'results' contains all the retrieved rows as dictionaries
        return {
            "previous": "",
            "next": "",
            "results": result,  # Include the list of results in the response
        }

        """
        if customer_name and potion_sku:
            # If both customer_name and potion_sku are provided, search with logical AND
            orders = connection.execute(
                sqlalchemy.text("
                    SELECT ci.id AS line_item_id, ci.sku AS item_sku, c.customer AS customer_name,
                        ci.quantity, p.cost, ci.created_at AS timestamp
                    FROM cart_items AS ci
                    JOIN carts AS c ON ci.cart_id = c.id
                    JOIN potions AS p ON ci.potion_id = p.id
                    WHERE c.customer = :customer_name AND p.sku = :potion_sku
                "),
                {"customer_name": customer_name, "potion_sku": potion_sku, "sort_col": sort_col}
            )
        else:
            # If not both customer_name and potion_sku are provided, search with logical AND
            orders = connection.execute(
                sqlalchemy.text("
                    SELECT ci.id AS line_item_id, ci.sku AS item_sku, c.customer AS customer_name,
                        ci.quantity, p.cost, ci.created_at AS timestamp
                    FROM cart_items AS ci
                    JOIN carts AS c ON ci.cart_id = c.id
                    JOIN potions AS p ON ci.potion_id = p.id
                    WHERE c.customer = :customer_name OR p.sku = :potion_sku
                "),
                {"customer_name": customer_name, "potion_sku": potion_sku, "sort_col": sort_col}
            )
        """

        """
        else:
            stmt = sqlalchemy.select([
                cart_items.c.id.label('line_item_id'),
                cart_items.c.sku.label('item_sku'),
                carts.c.customer.label('customer_name'),
                cart_items.c.quantity,
                potions.c.cost,
                cart_items.c.created_at.label('timestamp')
            ]).select_from(
                cart_items.join(carts, cart_items.c.cart_id == carts.c.id)
                        .join(potions, cart_items.c.potion_id == potions.c.id)
            )
            stmt = stmt.order_by(sort_col.asc()) if sort_order == "asc" else stmt.order_by(sort_col.desc())

            # Execute the query
            results = connection.execute(stmt)
        """
    """
        return {
            "previous": "",
            "next": "",
            "results": [
                {
                    "line_item_id": 1,
                    "item_sku": "1 oblivion potion",
                    "customer_name": "Scaramouche",
                    "line_item_total": 50,
                    "timestamp": "2021-01-01T00:00:00Z",
                }
            ],
        }
    """

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
                    num_christmas_potions += cart_item.quantity
                case 2:
                    num_red_potions += cart_item.quantity
                case 3:
                    num_blue_potions += cart_item.quantity
                case 4:
                    num_dark_potions += cart_item.quantity
                case 5:
                    num_green_potions += cart_item.quantity
                case 6:
                    num_purple_potions += cart_item.quantity
                case 7:
                    num_cyan_potions += cart_item.quantity

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