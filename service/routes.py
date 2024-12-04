######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Item Wishlist Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlist from the inventory of wishlists in the WishlistShop

"""

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, inputs

from service.models import Wishlist, Items
from service.common import status  # HTTP Status Codes
from . import api

######################################################################
# Wishlist Store Service with Swagger
# Paths:
# GET / - Displays a UI for Selenium testing
# GET /wishlists - Returns a list all of the Wishlists
# GET /wishlists/{id} - Returns the Wishlist with a given id number
# POST /wishlists - creates a new Wishlist record in the database
# PUT /wishlists/{id} - updates a Wishlist record in the database
# DELETE /wishlists/{id} - deletes a Wishlist record in the database
######################################################################


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Health check endpoint: Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")
    # return app.send_static_file("index.html")


# For Requirement 5
# Define the model so that the docs reflect what can be sent

create_item_model = api.model(
    "Item",
    {
        "name": fields.String(required=True, description="The name of the item"),
        "category": fields.String(
            required=False, description="The category of the item"
        ),
        "price": fields.Float(
            required=False, description="The price of the item (Floating Points)"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the items (Integers)"
        ),
        "is_favorite": fields.Boolean(
            required=False,
            description="Is the item marked as favorite? (Choose YES or NO)",
        ),
        "note": fields.String(required=False, description="Notes for the Items"),
        "wishlist_id": fields.Integer(
            required=True, description="The ID of the wishlist this item belongs to"
        ),
    },
)


item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {"id": fields.Integer(readOnly=True, description="The unique ID of the item")},
)

##
"""

"""
create_wishlist_model = api.model(
    "Wishlist",
    {
        "name": fields.String(required=True, description="The name of the wishlist"),
        "category": fields.String(
            required=True, description="The category of the wishlist"
        ),
        "is_favorite": fields.Boolean(
            required=True,
            description="Is the wishlist marked as favorite? (Choose YES or NO)",
        ),
        "updated_time": fields.String(
            required=False,
            description="The last updated timestamp (%a, %d %b %Y %H:%M:%S GMT) -> Example : Tue, 03 Dec 2024 15:18:50 GMT",
        ),
        "note": fields.String(required=False, description="Notes for the Wishlist"),
        "items": fields.List(fields.Nested(item_model), description="List of items"),
    },
)


wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {"id": fields.Integer(readOnly=True, description="The unique ID of the wishlist")},
)

# query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="List Wishlists by name"
)
wishlist_args.add_argument(
    "is_favorite",
    type=inputs.boolean,
    location="args",
    help="Filter items by favorite status",
)
wishlist_args.add_argument(
    "available",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Wishlists by availability",
)


item_args = reqparse.RequestParser()
item_args.add_argument("name", type=str, location="args", help="Filter items by name")
item_args.add_argument(
    "category", type=str, location="args", help="Filter items by category"
)
item_args.add_argument(
    "price", type=float, location="args", help="Filter items by price"
)
item_args.add_argument(
    "is_favorite",
    type=inputs.boolean,
    location="args",
    help="Filter items by favorite status",
)


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


# WISHLIST PART


######################################################################
#  PATH: /wishlists
######################################################################
# List wishlist
@api.route("/wishlists", strict_slashes=False)
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    # ------------------------------------------------------------------
    # LIST ALL WISHLISTS
    # ------------------------------------------------------------------
    @api.doc("list_wishlists")
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """Return list of all Wishlists"""
        wls = []

        is_favorite = request.args.get("is_favorite")
        name = request.args.get("name")
        # Parse any arguments from the query string
        if is_favorite:
            app.logger.info("Find by is_favorite: %s", is_favorite)
            # create bool from string
            is_favorite_value = is_favorite.lower() in ["true", "yes", "1"]
            wls = Wishlist.find_by_favorite(is_favorite_value)
        elif name:
            app.logger.info("Find by name: %s", name)
            name_value = name
            wls = Wishlist.find_by_name(name_value)
        else:
            app.logger.info("Find all")
            wls = Wishlist.all()
        results = [wl.serialize() for wl in wls]
        app.logger.info("Returning %d WLs", len(results))

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW WISHLIST
    # ------------------------------------------------------------------
    @api.doc("create_wishlists")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Create a Wishlist

        This endpoint will create a Wishlist based the data in the body that is posted
        """
        app.logger.info("Request to Create a Wishlist...")
        check_content_type("application/json")

        wishlist = Wishlist()
        # Get the data from the request and deserialize it
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        wishlist.deserialize(data)

        # Save the new Wishlist to the database
        wishlist.create()
        app.logger.info("Wishlist with new id [%s] saved!", wishlist.id)

        location_url = url_for(
            "wishlist_resource", wishlist_id=wishlist.id, _external=True
        )

        return (
            wishlist.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /wishlists/{id}
######################################################################
@api.route("/wishlists/<int:wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """Wishlist Class Function"""

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlists")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist

        This endpoint will return a Wishlist based on it's id
        """
        app.logger.info("Request for Wishlist with id: %s", wishlist_id)

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING Wishlist
    # ------------------------------------------------------------------
    @api.doc("update_wishlists")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist

        This endpoint will update a Wishlist based the body that is posted
        """
        app.logger.info("Request to Update a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        wishlist.deserialize(data)
        wishlist.id = wishlist_id
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("delete_wishlists")
    @api.response(204, "All Wishlists deleted")
    def delete(self, wishlist_id):
        """
        Delete a Wishlist
        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

        # Retrieve the wishlist to delete and delete it if it exists
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
        return "", status.HTTP_204_NO_CONTENT


# ITEMS


######################################################################
#  PATH: /wishlists/{id}/items
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items")
@api.param("item_id", "The Item identifier")
class ItemCollection(Resource):
    """
    Handles all interactions with collections of Items
    """

    # ------------------------------------------------------------------
    # CREATE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("create_items")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, wishlist_id):
        """
        Create an Item on an Wishlist

        This endpoint will add an item to an wishlist
        """
        app.logger.info(
            "Request to create an Item for Wishlist with id: %s", wishlist_id
        )
        check_content_type("application/json")

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Create an item from the json data
        item = Items()
        item.deserialize(request.get_json())

        # Append the item to the wishlist
        wishlist.items.append(item)
        wishlist.update()

        # Prepare a message to return
        message = item.serialize()

        # Send the location to GET the new item
        location_url = url_for(
            "item_resource", wishlist_id=wishlist.id, item_id=item.id, _external=True
        )
        return message, status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # LIST ALL ITEMS
    # ------------------------------------------------------------------
    @api.doc("list_items")
    @api.expect(item_args, validate=True)
    @api.marshal_list_with(item_model)
    def get(self, wishlist_id):
        """
        Get all Items in WL
        """
        item_name = request.args.get("name", default=None)
        category = request.args.get("category")
        price = request.args.get("price", type=float)
        is_favorite = request.args.get("is_favorite")
        app.logger.info(
            "Request to create an Item for Wishlist with id: %s", wishlist_id
        )
        wishlist = Wishlist.find(wishlist_id)
        items = wishlist.items
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )
        if item_name:
            app.logger.info("Searching for item by name: %s", item_name)
            # Convert `items` to a list of serialized dictionaries temporarily for name filtering
            filtered_items = [
                item.serialize()
                for item in items
                if item.name.lower() == item_name.lower()
            ]
            if not filtered_items:
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"Item with name '{item_name}' could not be found in Wishlist with id '{wishlist_id}'.",
                )

        if category:
            app.logger.info("Filtering by category: %s", category)
            items = Items.find_by_category(wishlist_id=wishlist_id, category=category)
        elif price is not None:
            app.logger.info("Filtering by price: %s", price)
            items = Items.find_by_price(wishlist_id=wishlist_id, price=price)
        elif is_favorite:
            app.logger.info("Find by is_favorite: %s", is_favorite)
            # create bool from string
            is_favorite_value = is_favorite.lower() in ["true", "yes", "1"]
            items = Items.find_by_favorite(wishlist_id, is_favorite_value)
        else:
            app.logger.info("Retrieving all items in wishlist")
            items = Items.all()

        results = [item.serialize() for item in items]
        app.logger.info("[%s] Items returned", len(results))
        return results, status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/{id}/items/{id}
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items/<int:item_id>")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """Item Class Function"""

    # ------------------------------------------------------------------
    # UPDATE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("update_items")
    @api.response(404, "Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id):
        """
        Update an Item in a Wishlist

        This endpoint will update an Item based on the body that is posted
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(404, description=f"Wishlist with id '{wishlist_id}' was not found.")

        item = Items.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            abort(
                404,
                description=f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
            )

        data = request.get_json()
        item.deserialize(data)

        # Ensure the ID is set before updating
        if not item.id:
            abort(status.HTTP_400_BAD_REQUEST, "Cannot update item with empty ID.")

        item.update()
        return item, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_items")
    @api.response(204, "Item deleted")
    def delete(self, wishlist_id, item_id):
        """
        Delete an Item from a Wishlist
        """
        app.logger.info("Deleting Item %s from Wishlist %s", item_id, wishlist_id)

        item = Items.find(item_id)
        if item:
            item.delete()
            app.logger.info("Item %s deleted successfully", item_id)

        return "", status.HTTP_204_NO_CONTENT

    # ------------------------------------------------------------------
    # GET AN ITEM
    # ------------------------------------------------------------------
    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """
        Get an Item

        This endpoint returns just an item
        """
        app.logger.info(
            "Request to retrieve Items %s for Wishlist id: %s", (item_id, wishlist_id)
        )

        # See if the item exists and abort if it doesn't
        item = Items.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{item_id}' could not be found.",
            )

        return item, status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


@api.route("/wishlists/<int:wishlist_id>/items/<int:item_id>/favorite")
@api.param("")
class ItemMarkFavoriteResource(Resource):
    """Wishlist Favorite Class Function"""

    @api.doc("mark_items_favorite")
    @api.response(404, "Items favorite not marked")
    def put(self, wishlist_id, item_id):
        """
        Mark an item as favorite in a wishlist
        """
        app.logger.info(
            "Request to mark item [%s] as favorite in Wishlist with id: %s",
            item_id,
            wishlist_id,
        )

        # Find the item and return 404 if not found
        item = Items.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        # Mark the item as favorite
        item.is_favorite = True
        item.update()
        app.logger.info(
            "Item [%s] marked as favorite in Wishlist [%s]", item_id, wishlist_id
        )

        return item.serialize(), status.HTTP_200_OK

    @api.doc("delete_items_favorite")
    @api.response(204, "Items favorite deleted")
    def delete(self, wishlist_id, item_id):
        """
        Cancel an item as favorite in a wishlist
        """
        app.logger.info(
            "Request to cancel item [%s] as favorite in Wishlist with id: %s",
            item_id,
            wishlist_id,
        )

        # Find the item and return 404 if not found
        item = Items.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        # Cancel the item as favorite
        item.is_favorite = False
        item.update()
        app.logger.info(
            "Item [%s] canceled as favorite in Wishlist [%s]", item_id, wishlist_id
        )

        return item.serialize(), status.HTTP_200_OK


@api.route("/wishlists/<int:wishlist_id>/favorite")
@api.param("")
class WishlistMarkFavoriteResource(Resource):
    """Item Favorite Class Function"""

    @api.doc("mark_items_favorite")
    @api.response(404, "Wishlists favorite not marked")
    def put(self, wishlist_id):
        """
        Mark an item as favorite in a wishlist
        """
        app.logger.info(
            "Request to mark wishlist [%s] as favorite",
            wishlist_id,
        )

        # Find the item and return 404 if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Mark the item as favorite
        wishlist.is_favorite = True
        wishlist.update()
        app.logger.info("Wishlist [%s] marked as favorite", wishlist_id)

        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc("delete_wishlist_favorite")
    @api.response(204, "Wishlists favorite deleted")
    def delete(self, wishlist_id):
        """
        Cancel an item as favorite in a wishlist
        """
        app.logger.info(
            "Request to cancel wishlist [%s] as favorite",
            wishlist_id,
        )

        # Find the item and return 404 if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Cancel the wishlist as favorite
        wishlist.is_favorite = False
        wishlist.update()
        app.logger.info("Wishlist [%s] canceled as favorite", wishlist_id)

        return wishlist.serialize(), status.HTTP_200_OK
