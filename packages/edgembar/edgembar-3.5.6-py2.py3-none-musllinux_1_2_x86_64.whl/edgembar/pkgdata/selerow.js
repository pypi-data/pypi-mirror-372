
function seleRow(rowid) {
    document.querySelectorAll('tbody tr').forEach( function(elem) {
	// console.log(elem,elem.className);
	if (elem.className.indexOf('selected') >= 0) {
	    elem.className = elem.className.replace("selected","");
	}
    });
    if ( rowid != undefined ) {
	let elem = document.getElementById(rowid);
	if ( elem != undefined ) {
	    elem.className += " selected";
	};
    };
}

