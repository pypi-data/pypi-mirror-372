
window.onload = function () { // After page loads
    Array.from(document.getElementsByTagName("th")).forEach((element, index) => { // Table headers
        element.addEventListener("click", function (event) {
            let table = this.closest("table");

	    let span_elems = this.getElementsByTagName("span");
            let order_icon = span_elems[span_elems.length-1];
	    //console.log(encodeURI(order_icon.innerHTML))
            //let order      = encodeURI(order_icon.innerHTML).includes("%E2%86%91") ? "desc" : "asc";
	    let uristr = encodeURI(order_icon.innerHTML);
	    let order = "";
	    if ( uristr.includes("%E2%86%91") ) {
		order = "desc";
	    }
	    else if ( uristr.includes("%E2%86%93") ) {
		order = "asc";
	    };
            let value_list = {}; // <tr> Object
            let obj_key    = []; // Values of selected column
            let separator  = "-----"; // Separate the value of it's index, so data keeps intact

            let string_count = 0;
            let number_count = 0;

            table.querySelectorAll("tbody tr").forEach((linha, index_line) => { // <tbody> rows
                let key = linha.children[element.cellIndex].textContent.toUpperCase();
                //key.replace("-", "").match(/^[0-9,.]*$/g) ? number_count++ : string_count++; // Check if value is numeric or string
		key.match(/^[0-9,.Ee-]*$/g) ? number_count++ : string_count++; // Check if value is numeric or string

                value_list[key + separator + index_line] = linha.outerHTML.replace(/(\t)|(\n)/g, ''); // Adding <tr> to object
                obj_key.push(key + separator + index_line);
            });

            if (number_count > 0 && string_count <= 0) { // If all values are numeric
                obj_key.sort(function(a, b) {
                    return parseFloat(a.split(separator)[0]) - parseFloat(b.split(separator)[0]);
                });
            }
            else {
                obj_key.sort();
            }

            if (order == "desc"){
                obj_key.reverse();
                order_icon.innerHTML = "&darr;";
            }
            else if (order == "asc") {
                order_icon.innerHTML = "&uarr;";
            }

            let html = "";
            obj_key.forEach(function (chave) {
                html += value_list[chave];
            });
            table.getElementsByTagName("tbody")[0].innerHTML = html;
        });
    });
}

