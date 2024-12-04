"""
Models for Wishlist

All of the models are stored in this module
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .items import Items


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()

######################################################################
#  W I S H L I S T   M O D E L
######################################################################


class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a Wishlist
    """

    ##################################################
    # Table Schema
    ##################################################

    __tablename__ = "wishlist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # wishlist id
    name = db.Column(db.String(100), nullable=False)  # wishlist name
    updated_time = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.String(1000), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)

    items = db.relationship("Items", backref="wishlist", passive_deletes=True)

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "name": self.name,
            "updated_time": (self.updated_time.strftime("%a, %d %b %Y %H:%M:%S GMT")),
            "note": self.note,
            "items": [],
            "is_favorite": self.is_favorite,
        }
        for item in self.items:
            wishlist["items"].append(item.serialize())

        return wishlist

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.updated_time = data["updated_time"]
            self.note = data["note"]
            self.is_favorite = data.get("is_favorite", False)

            # handle inner list of addresses
            item_list = data.get("items")
            for json_item in item_list:
                item = Items()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Wishlists in the database"""
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Wishlist by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_by_favorite(cls, is_favorite: bool = True) -> list:
        """Returns all Wishlists by their is_favorite

        :param is_favorite: True for wishlists that are favorite
        :type favorite: str

        :return: a collection of Items that are favorite
        :rtype: list

        """
        if not isinstance(is_favorite, bool):
            raise TypeError("Invalid availability, must be of type boolean")
        logger.info("Processing favorite query for %s ...", is_favorite)
        return cls.query.filter(cls.is_favorite == is_favorite)
