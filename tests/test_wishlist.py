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
Test cases for Wishlist Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from service.models import Wishlist, Items, db, DataValidationError
from wsgi import app
from tests.factories import WishlistFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Wishlist   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()
        db.session.query(Items).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_create_a_wishlist(self):
        """It should create a Wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        found = Wishlist.all()
        self.assertEqual(len(found), 1)
        data = Wishlist.find(wishlist.id)
        self.assertEqual(data.name, wishlist.name)
        self.assertEqual(data.updated_time, wishlist.updated_time)
        self.assertEqual(data.note, wishlist.note)
        self.assertEqual(data.is_favorite, wishlist.is_favorite)

    @patch("service.models.db.session.commit")
    def test_create_a_wishlist_failed(self, exception_mock):
        """It should not create an Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.create)

    def test_create_wishlist_with_null_name(self):
        """It should fail to create a Wishlist with a null name and raise DataValidationError"""
        test_wishlist = WishlistFactory()
        test_wishlist.name = None
        with self.assertRaises(DataValidationError) as context:
            test_wishlist.create()
        self.assertIn("null value in column", str(context.exception))
        self.assertIn("violates not-null constraint", str(context.exception))
        result = Wishlist.query.filter_by(name=None).first()
        self.assertIsNone(result)

    def test_update_a_wishlist(self):
        """It should Update a Wishlist"""
        wishlist = WishlistFactory(name="Swimming")
        logging.debug(wishlist)
        wishlist.id = None
        wishlist.create()
        logging.debug(wishlist)
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(wishlist.name, "Swimming")
        # Change it an save it
        wishlist = Wishlist.find(wishlist.id)
        original_id = wishlist.id
        wishlist.name = "Biking"
        wishlist.update()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.name, "Biking")
        self.assertEqual(wishlist.id, original_id)

    def test_update_no_id(self):
        """It should not Update a Wishlist with no id"""
        wishlist = WishlistFactory()
        logging.debug(wishlist)
        wishlist.id = None
        self.assertRaises(DataValidationError, wishlist.update)

    @patch("service.models.db.session.commit")
    def test_update_wishlist_failed(self, exception_mock):
        """It should not update a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.update)

    def test_delete_a_wishlist(self):
        """It should Delete a Wishlist"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        wishlist = wishlists[0]
        wishlist.delete()
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 0)

    @patch("service.models.db.session.commit")
    def test_delete_a_wishlist_failed(self, exception_mock):
        """It should not delete an Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.delete)

    def test_find_by_name(self):
        """It should Find an Wishlist by name"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.name, wishlist.name)

    def test_deserialize_with_wishlist_key_error(self):
        """It should not Deserialize a wishlist with a KeyError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_wishlist_type_error(self):
        """It should not Deserialize a wishlist with a TypeError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_deserialize_valid_items(self):
        """It should correctly deserialize a Wishlist with valid items"""
        # add category
        data = {
            "id": 100,
            "name": "My Wishlist",
            "updated_time": "2024-01-01 12:00:00",
            "note": "This is a sample note",
            "items": [
                {
                    "id": 1,
                    "name": "Item 1",
                    "quantity": 2,
                    "category": "electronics",
                    "price": 19.99,
                },
                {
                    "id": 2,
                    "name": "Item 2",
                    "quantity": 5,
                    "category": "books",
                    "price": 39.99,
                },
            ],
        }
        wishlist = WishlistFactory()
        wishlist.deserialize(data)

        # Check if the wishlist attributes are correctly deserialized
        self.assertEqual(wishlist.name, data["name"])
        self.assertEqual(wishlist.note, data["note"])
        self.assertEqual(len(wishlist.items), 2)  # Two items should be deserialized
        self.assertEqual(wishlist.items[0].name, "Item 1")
        self.assertEqual(wishlist.items[0].quantity, 2)
        self.assertEqual(wishlist.items[0].category, "electronics")
        self.assertEqual(wishlist.items[0].price, 19.99)

        self.assertEqual(wishlist.items[1].name, "Item 2")
        self.assertEqual(wishlist.items[1].quantity, 5)
        self.assertEqual(wishlist.items[1].category, "books")
        self.assertEqual(wishlist.items[1].price, 39.99)

    def test_find_by_favorite(self):
        """It should Find Wishlists by Favorite"""
        wishlists = WishlistFactory.create_batch(10)
        for wishlist in wishlists:
            wishlist.create()
        is_favorite = wishlists[0].is_favorite
        count = len(
            [wishlist for wishlist in wishlists if wishlist.is_favorite == is_favorite]
        )
        found = Wishlist.find_by_favorite(is_favorite)
        self.assertEqual(found.count(), count)
        for wishlist in found:
            self.assertEqual(wishlist.is_favorite, is_favorite)
