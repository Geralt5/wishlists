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
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  I T E M S   M O D E L
######################################################################
class Items(db.Model, PersistentBase):
    """
    Class that represents an Address
    """

    # Table Schema
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)  # id of each item
    wishlist_id = db.Column(
        db.Integer, db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(1000), nullable=True)
    category = db.Column(db.String(100), nullable=False)  # category
    price = db.Column(db.Float, nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)

    def serialize(self):
        """
        Serializes an Item into a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "note": self.note,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "wishlist_id": self.wishlist_id,
            "is_favorite": self.is_favorite,
        }

    def deserialize(self, data):
        """
        Deserializes an Item from a dictionary
        """
        try:
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.category = data["category"]
            self.price = data["price"]
            self.note = data.get("note", "")
            self.is_favorite = data.get("is_favorite", False)

        except KeyError as error:
            raise DataValidationError(
                "Invalid Address: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def find_by_price(cls, wishlist_id, price):
        """Returns all Wishlists with the given name

        Args:
            price (float): the price  of the Wishlists item you want to match
        """
        logger.info(
            "Processing query for wishlist_id=%s and price=%s ...", wishlist_id, price
        )
        return cls.query.filter(
            cls.wishlist_id == wishlist_id, cls.price == price
        ).all()

    @classmethod
    def find_by_category(cls, wishlist_id, category):
        """Returns all Wishlists with the given name

        Args:
            category (string): the category of the Wishlists item you want to match
        """
        logger.info(
            "Processing query for wishlist_id=%s and price=%s ...",
            wishlist_id,
            category,
        )
        return cls.query.filter(
            cls.wishlist_id == wishlist_id, cls.category == category
        ).all()

    @classmethod
    def find_by_favorite(cls, wishlist_id, is_favorite: bool = True) -> list:
        """Returns all Items by their is_favorite

        :param is_favorite: True for items that are favorite
        :type favorite: str

        :return: a collection of Items that are favorite
        :rtype: list

        """
        if not isinstance(is_favorite, bool):
            raise TypeError("Invalid availability, must be of type boolean")
        logger.info("Processing favorite query for %s ...", is_favorite)
        return cls.query.filter(
            cls.wishlist_id == wishlist_id, cls.is_favorite == is_favorite
        )

    # The following code will cause errors for the Items RestAPI
