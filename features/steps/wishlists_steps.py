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
Wishlist Steps

Steps file for Pet.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
from datetime import datetime
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following wishlists")
def step_impl(context):
    """Delete all Wishlists and load new ones"""

    # Get a list all of the wishlists
    rest_endpoint = f"{context.base_url}/api/wishlists"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # Delete existing wishlists
    for wishlist in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{wishlist['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load the database with new wishlists
    for row in context.table:
        # Convert `updated_time` to required format
        try:
            formatted_time = datetime.strptime(
                row["updated_time"], "%Y-%m-%d"
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except ValueError as e:
            raise ValueError(
                f"Invalid date format in 'updated_time': {row['updated_time']}"
            ) from e

        payload = {
            "name": row["name"],
            "updated_time": formatted_time,  # Use the formatted date
            "note": row["note"],
            "is_favorite": row["is_favorite"] in ["True", "true", "1"],
            "items": [],
        }

        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        if context.resp.status_code != HTTP_201_CREATED:
            print("POST Error:", context.resp.status_code, context.resp.json())
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
