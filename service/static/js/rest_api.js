$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_wishlist_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_note").val(res.note);

        if (res.is_favorite == true) {
            $("#wishlist_favorite").val("true");
        } else {
            $("#wishlist_favorite").val("false");
        }
        // make updated_time to date struct
        let date = new Date(res.updated_time);
        let formattedDate = date.toISOString().split('T')[0]; // extract YYYY-MM-DD part
        $("#wishlist_update").val(formattedDate);
    }

    // Clears all form fields
    function clear_wishlist_data() {
        $("#wishlist_name").val("");
        $("#customer_name").val("");
        $("#wishlist_favorite").val("");
        $("#wishlist_note").val("");
        $("#wishlist_update").val("");
    }

    //Clear the wishlist
    $("#wishlist_clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_wishlist_data()
    });

    // Updates the form with data from the response
    function update_item_data(res) {
        $("#item_id").val(res.id);
        $("#item_name").val(res.name);
        $("#item_category").val(res.category);
        $("#item_quantity").val(res.quantity);
        $("#item_price").val(res.price);

        $("#item_note").val(res.note);

        if (res.is_favorite == true) {
            $("#item_favorite").val("true");
        } else {
            $("#item_favorite").val("false");
        }
        $("#item_update").val(res.updated_time);
    }

    // Clear all form fields
    function clear_item_data() {
        $("#item_name").val("");
        $("#customer_name").val("");
        $("#item_favorite").val("");
        $("#item_note").val("");
        $("#item_update").val("");
        $("#item_category").val("");
        $("#item_price").val("");
        $("#item_quantity").val("");
    }
    
    // Update the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }


    // WISHLIST //

    // Retrieve a Wishlist
    $("#wishlist_retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res) {
            //alert(res.toSource())
            update_wishlist_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_wishlist_data()
            flash_message("404 Not Found")
        });

    });

    // Create a Wishlist
    $("#wishlist_create-btn").click(function () {

        let name = $("#wishlist_name").val();
        let note = $("#wishlist_note").val();
        let update = $("#wishlist_update").val(); 
        let is_favorite = $("#wishlist_favorite").prop("checked");
        
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "POST",
            url: "/api/wishlists",
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                note: note,
                updated_time: new Date(update).toISOString(),
                items: [],
                is_favorite: is_favorite
            })
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_wishlist_data()
            flash_message(res.responseJSON.message)
        });

    });

    // Update the Wishlist
    $("#wishlist_update-btn").click(function () {
        let wishlist_id = $("#wishlist_id").val();
        let name = $("#wishlist_name").val();
        let note = $("#wishlist_note").val();
        let update = $("#wishlist_update").val(); 
        let is_favorite = $("#item_favorite").prop("checked");


        
        
        $("#flash_message").empty();
        
        if (!wishlist_id) {
            alert("Wishlist ID is required to update the resource.");
            return;
        }
        
        let ajax = $.ajax({
            type: "PUT",
            url: `/api/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                note: note,
                updated_time: new Date(update).toISOString(),
                items: [],
                is_favorite: is_favorite
            })
        });

        ajax.done(function(res){
            update_wishlist_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_wishlist_data()
            flash_message(res.responseJSON.message)
        });

    });

    // Clear the wishlist interface
    $("#wishlist_clear_int-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });

    // Search for a WL
    // ****************************************

    $("#wishlist_search-btn").click(function () {

        let name = $("#wishlist_name").val();
        let category = $("#pet_category").val();
        let available = $("#pet_available").val() == "true";

        let queryString = "";
        if (name) {
            queryString += 'name=' + name
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Note</th>'
            table += '<th class="col-md-2">Favorite?</th>'
            table += '<th class="col-md-2">Updated Time</th>'
            table += '</tr></thead><tbody>'
            let firstWL = "";
            
            for(let i = 0; i < res.length; i++) {
                let WL = res[i];
                let date = new Date(WL.updated_time);
                let formattedDate = date.toISOString().split('T')[0];
                table +=  `<tr id="row_${i}"><td>${WL.id}</td><td>${WL.name}</td><td>${WL.note}</td><td>${WL.is_favorite}</td><td>${formattedDate}</td><td>`;
                if (i == 0) {
                    firstWL = WL;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);
            //flash_message(str(firstWL))
            // copy the first result to the form
            if (firstWL != "") {
                update_wishlist_data(firstWL)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#wishlist_delete-btn").click(function () {

        let id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/${id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res) {
            console.log("Delete response:", res);
            clear_form_data();
            flash_message("Wishlist deleted successfully!");
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ITEM //

    // CREATE an Item in the wishlist
    $("#item_create-btn").click(function () {
        let name = $("#item_name").val();
        let category = $("#item_category").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();
        let update = $("#item_update").val(); 
        let note = $("#item_note").val();
        let is_favorite = $("#item_favorite").prop("checked");
        let wishlist_id = $("#desired_item_wishlist").val();
    
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/api/wishlists/${wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                category: category,
                quantity: quantity,
                price: price,
                note: note,
                updated_time: update,
                is_favorite: is_favorite
            })
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_item_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_item_data()
            flash_message(res.responseJSON.message)
        });

    });

    // UPDATE an Item in the wishlist
    $("#item_update-btn").click(function () {
        let item_id = $("#item_id").val();
        let name = $("#item_name").val();
        let category = $("#item_category").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();
        let update = $("#item_update").val();
        let note = $("#item_note").val();
        let is_favorite = $("#item_favorite").prop("checked");
        let wishlist_id = $("#desired_item_wishlist").val();
    
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "PUT",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                category: category,
                quantity: quantity,
                price: price,
                note: note,
                updated_time: update,
                is_favorite: is_favorite
            })
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_item_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_item_data()
            flash_message(res.responseJSON.message)
        });

    });

    // LIST items in the wishlist
    $("#item_search-btn").click(function () {

        let I_name = $("#item_name").val();
        let wish_id = $("#desired_item_wishlist").val();
        let category = $("#item_category").val(); 
        let price = $("#item_price").val();

        let queryString = ""

        if (!wishlist_id) {
            flash_message("Please provide a Wishlist ID.");
            return;
        }

        if (I_name) {
            queryString += "name=" + encodeURIComponent(name);
        }
        if (category) {
            queryString += "category=" + encodeURIComponent(category);
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += "&";
            }
            queryString += "price=" + encodeURIComponent(price);
        }
        flash_message(queryString)

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wish_id}/items${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results_items").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Wishlist</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Favorite?</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Note</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '</tr></thead><tbody>'
            $("#wishlist_note").val(res.note);
            update_item_data(res)
            let firstItm = "";
            //for(let i = 0; i < res.length; i++)
            //let itm = res[i];
                
            table +=  `<tr id="row_${i}"><td>${res.id}</td><td>${res.wishlist_id}</td><td>${res.category}</td><td>${res.is_favorite}</td><td>${res.name}</td><td>${res.note}</td></tr>${res.quantity}</td><td>${res.price}</td></tr>`;

            table += '</tbody></table>';
            $("#search_results_items").append(table);

            // copy the first result to the form
            /*
            if (firstPet != "") {
                update_form_data(firstPet)
            }
            */
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // DELETE items in the wishlist
    $("#item_delete-btn").click(function () {

        let id = $("#item_id").val();
        let wishlist_id = $("#desired_item_wishlist").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // QUERY all the items in different wishlists
    $("#item_query-btn").click(function () {
        let name = $("#item_name").val();
        let category = $("#item_category").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();
        let update = $("#item_update").val();
        let is_favorite = $("#item_favorite").prop("checked");
        
        $("#flash_message").empty();
    
        // Build the query string dynamically
        let queryParams = [];
        if (name) queryParams.push(`name=${encodeURIComponent(name)}`);
        if (category) queryParams.push(`category=${encodeURIComponent(category)}`);
        if (quantity) queryParams.push(`quantity=${encodeURIComponent(quantity)}`);
        if (price) queryParams.push(`price=${encodeURIComponent(price)}`);
        if (update) queryParams.push(`updated_time=${encodeURIComponent(update)}`);
        if (is_favorite) queryParams.push(`is_favorite=${is_favorite}`);
    
        let queryString = queryParams.length > 0 ? `?${queryParams.join("&")}` : "";
    
        let ajax = $.ajax({
            type: "GET",
            url: `/api/items${queryString}`,
            contentType: "application/json"
        });
    
        ajax.done(function (res) {
            console.log("Query Results:", res);
            $("#flash_message").text(`Found ${res.length} items matching the criteria`);
        });
    
        ajax.fail(function (xhr, status, error) {
            console.error("Query Failed:", error);
            $("#flash_message").text(`Error querying items: ${xhr.responseText}`);
        });
    });
    
     // CLEAR the items interface
     $("#item_clear-btn").click(function () {
        $("#item_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });

    $("#item_search-btn").click(function () {
        let wishlist_id = $("#wishlist_id").val(); 
        let category = $("#item_category").val(); 
        let price = $("#item_price").val();  
        let name = $("#item_name").val();     

        if (!wishlist_id) {
            flash_message("Please provide a Wishlist ID.");
            return;
        }
    
        let queryString = "";
        if (name) {
            queryString += "name=" + encodeURIComponent(name);
        }
        if (category) {
            queryString += "category=" + encodeURIComponent(category);
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += "&";
            }
            queryString += "price=" + encodeURIComponent(price);
        }
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wishlist_id}/items?${queryString}`, // Use the specified route
            contentType: "application/json",
            data: "",
        });
    
        ajax.done(function (res) {
            $("#search_results").empty();
    
            let table = `
                <table class="table table-striped" cellpadding="10">
                    <thead>
                        <tr>
                            <th class="col-md-2">Item ID</th>
                            <th class="col-md-2">Name</th>
                            <th class="col-md-2">Category</th>
                            <th class="col-md-2">Price</th>
                            <th class="col-md-2">Quantity</th>
                            <th class="col-md-2">Wishlist ID</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
    
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `
                    <tr id="row_${i}">
                        <td>${item.id}</td>
                        <td>${item.name}</td>
                        <td>${item.category}</td>
                        <td>${item.price}</td>
                        <td>${item.quantity}</td>
                        <td>${item.wishlist_id}</td>
                    </tr>
                `;
            }
            table += "</tbody></table>";
            $("#search_results").append(table);
    
            flash_message("Items retrieved successfully!");
        });
    
        ajax.fail(function (res) {
            const errorMessage = res.responseJSON?.message || "Error occurred while fetching results.";
            flash_message(errorMessage);
        });
    });
})
