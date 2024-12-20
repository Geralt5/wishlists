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
Test cases for item Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Wishlist, Items, db, DataValidationError
from tests.factories import WishlistFactory, ItemsFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  I T E M S  M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(TestCase):
    """Items Model Test Cases"""

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
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(Items).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_create_items(self):
        """It should create a new Item in the Wishlist"""

        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        item = ItemsFactory(wishlist=wishlist)
        wishlist.items.append(item)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(new_wishlist.items[0].name, item.name)
        self.assertEqual(new_wishlist.items[0].is_favorite, item.is_favorite)

        item2 = ItemsFactory(wishlist=wishlist)
        wishlist.items.append(item2)
        wishlist.update()

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(new_wishlist.items), 2)
        self.assertEqual(new_wishlist.items[1].name, item2.name)
        self.assertEqual(new_wishlist.items[1].is_favorite, item2.is_favorite)

    def test_delete_items(self):
        """It should Delete an item from a Wishlist"""
        wishlist = WishlistFactory()
        item = ItemsFactory(wishlist=wishlist)
        wishlist.items.append(item)
        wishlist.create()

        # Confirmation that the item exists in the wish list
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(len(wishlist.items), 1)
        self.assertEqual(wishlist.items[0].id, item.id)

        # Delete items and update the wishlist
        item.delete()
        wishlist.update()

        # Retrieve the wish list from the database and confirm that the item has been deleted
        updated_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(updated_wishlist.items), 0)
        self.assertIsNone(Items.find(item.id))

    def test_update_wishlist_item(self):
        """It should Update a Wishlist Item"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        item = ItemsFactory(wishlist=wishlist)
        wishlist.items.append(item)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        old_item = wishlist.items[0]
        self.assertEqual(old_item.note, item.note)
        # Change the note
        old_item.note = "Updated"
        old_item.category = "Food"  # category
        old_item.quantity = 7
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        item = wishlist.items[0]
        self.assertEqual(item.note, "Updated")
        self.assertEqual(item.category, "Food")
        self.assertEqual(item.quantity, 7)

    def test_update_wishlist_item_invalid_quantity(self):
        """It should fail to Update a Wishlist Item with invalid quantity type"""
        wishlist = WishlistFactory()
        item = ItemsFactory(wishlist=wishlist)
        wishlist.items.append(item)
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        wishlist = Wishlist.find(wishlist.id)
        old_item = wishlist.items[0]
        old_item.note = "Updated"
        old_item.quantity = "invalid"
        old_item.category = "Food"
        with self.assertRaises(DataValidationError):
            wishlist.update()

    def test_read_items(self):
        """It should Read a Item"""
        item = ItemsFactory()
        logging.debug(item)
        item.id = None
        item.create()
        self.assertIsNotNone(item.id)
        # Fetch it back
        found_item = item.find(item.id)
        self.assertEqual(found_item.id, item.id)
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.quantity, item.quantity)
        self.assertEqual(found_item.category, item.category)
        self.assertEqual(found_item.note, item.note)

    def test_find_by_price(self):
        """It should find Items by Price"""
        wishlist = WishlistFactory()
        item1 = ItemsFactory(price=20.5, wishlist=wishlist)
        item2 = ItemsFactory(price=50.0, wishlist=wishlist)
        wishlist.items.append(item1)
        wishlist.items.append(item2)
        wishlist.create()

        items = Items.find_by_price(wishlist_id=wishlist.id, price=20.5)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].price, 20.5)
        self.assertEqual(items[0].name, item1.name)

    def test_find_by_category(self):
        """It should find Items by Category"""
        wishlist = WishlistFactory()
        item1 = ItemsFactory(category="food", wishlist=wishlist)
        item2 = ItemsFactory(category="electronics", wishlist=wishlist)
        wishlist.items.append(item1)
        wishlist.items.append(item2)
        wishlist.create()

        items = Items.find_by_category(wishlist_id=wishlist.id, category="food")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].category, "food")
        self.assertEqual(items[0].name, item1.name)

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Items()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Items()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_find_by_favorite(self):
        """It should Find Items by is_favorite"""

        # Ensure no wishlists exist initially
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        # Create a new wishlist and add it to the database
        wishlist = WishlistFactory()
        wishlist.create()

        # Assert that the wishlist has been created and has an ID
        self.assertIsNotNone(wishlist.id)

        # Create 10 items associated with the created wishlist
        items = ItemsFactory.create_batch(10, wishlist=wishlist)
        for item in items:
            db.session.add(item)

        db.session.add(wishlist)
        db.session.commit()
        # Check that we have 10 items in the database for the wishlist
        self.assertEqual(len(Items.all()), 10)

        # Find and count items with a specific `is_favorite` status
        is_favorite = items[0].is_favorite
        count = len([item for item in items if item.is_favorite == is_favorite])
        found = Items.find_by_favorite(wishlist.id, is_favorite)

        # Verify that the number of found items matches the expected count
        self.assertEqual(found.count(), count)
        for item in found:
            self.assertEqual(item.is_favorite, is_favorite)
