
/* 
   This script assumes that several global variables have been defined
   elsewhere.  From this data, it will setup a vis-network display and
   callback functions to dynamically set the visual properties.

   Ideally, I'd rewrite this to be a javascript class and these global
   variables would instead be the argument to the object's initializer;
   however, I don't immediately see a scenerio where multiple graphs
   would be displayed on the same webpage, so global variables will be
   fine for the time being.

   gnodes : a list of strings
       The node id values, e.g.,
       var gnodes = ["lig1","lig2","lig3"];

   gedges : a list of strings
       The edge id values, e.g.,
       var gedges = ["lig1~lig2","lig1~lig3"];

   gnode_def : a dict of default node properties
       The keys are color and size, e.g.,
       var gnode_def = { color: "rgb(100,100,200)", size: 1 };

   gedge_def : a dict of default edge properties
       The keys are color and size, e.g.,
       var gedge_def = { color: "rgb(0,0,0)", size: 1 };

   gdata : a dict of edge and node properties
       The keys are the node and edge id values
       The values are a dict, whose keys represent the "scheme", e.g.,
       var gdata = {
           "lig1": {
	       CONFE: { color: "rgb(0,0,255)", size: 1 },
	       UNCONFE: { color: "rgb(0,0,255)", size: 1 }
	   } }

*/


/* Returns a copy of a simple object, like a list of dict */

const deepCopyFunction = (inObject) => {
    let outObject, value, key;

    if (typeof inObject !== "object" || inObject === null) {
	return inObject; // Return the value if inObject is not an object
    };

    // Create an array or object to hold the values
    outObject = Array.isArray(inObject) ? [] : {};
    
    for (key in inObject) {
	value = inObject[key];
	
	// Recursively (deep) copy for nested objects, including arrays
	outObject[key] = deepCopyFunction(value);
    };
    return outObject;
}




/* Given a list, find the index of the element whose id attribute matches
   a value */

function getIdIndex(obj,value) {
    for (var i=0; i < obj.length; i++) {
	if ( obj[i].id == value ) {
	    return i;
	}
    }
}



/* When the user clicks on the Properties formfield, show the checked table
   and reset the graph display to a solid representation */

function showTable(tableId) {
    setSolid();
    dispUpdate();
    document.querySelectorAll('.hidable').forEach( function(elem) {
	elem.style.display='none';
    });
    document.getElementById(tableId).style.display='block';
}



/* Redraw the display using the current set of node and edge properties */

function dispUpdate() {
    nodes.update( nodeopts_current );
    edges.update( edgeopts_current );
}



/* This sets the current set of node and edge opacity values to 1,
   but it does not redraw the display (use dispUpdate to update the
   display) */

function setSolid() {
    setSolidNodes();
    setSolidEdges();
}



/* This sets the node opacity values to 1 for the specified nodes,
   but it does not redraw the display (use dispUpdate to update the
   display).  The input is a list of string id values. */

function setSolidNodes(nodeIds) {
    nodeopts_current.forEach( function(opt) {
	if ( nodeIds == undefined ) {
	    opt.opacity=1;
	} else {
	    if ( nodeIds.includes( opt.id ) ) {
		opt.opacity=1;
	    };
	}
    });
};


/* This sets the current set of edge opacity values to 1,
   but it does not redraw the display (use dispUpdate to update the
   display). The input is a list of string id values. */

function setSolidEdges(edgeIds) {
    edgeopts_current.forEach( function(opt) {
	if ( edgeIds == undefined ) {
	    opt.color.opacity=1;
	} else {
	    if ( edgeIds.includes( opt.id ) ) {
		opt.color.opacity=1;
	    };
	}		  
    });
};



/* This sets the opacity of all edges and nodes to 0.2, but it does 
   not redraw the display (use dispUpdate to update the display) */

function setTransparent() {
    nodeopts_current.forEach( function(opt) {
	opt.opacity=0;
    });
    
    edgeopts_current.forEach( function(eopt) {
	eopt.color.opacity = 0.2;
    });
};



/* Set all node and edge properties to their default values */

function setDefault() {
    setNodeColors("DEF");
    setEdgeColors("DEF");
    setEdgeSizes("DEF");
}



/* Set the node colors for the specified scheme. This does not redraw the
   display. The input scheme is a string (a key within the global graph data) */

function setNodeColors(ncprop) {
    nodeopts_current.forEach( function(p) {
	let nc = gdata[p.id][ncprop] ?? {color:gnode_def.color};
	p.color.background = nc.color;
	p.color.highlight.background = nc.color;
	p.color.hover.background = nc.color;
    });
}



/* Set the edge colors for the specified scheme. This does not redraw the
   display. The input scheme is a string (a key within the global graph data) */

function setEdgeColors(ecprop) {
    edgeopts_current.forEach( function(p) {
	let ec = gdata[p.id][ecprop] ?? {color:gedge_def.color};
	p.color.color = ec.color;
	p.color.highlight = p.color.color;
    });
}



/* Set the edge sizes for the specified scheme. This does not redraw the
   display. The input scheme is a string (a key within the global graph data) */

function setEdgeSizes(esprop) {
    edgeopts_current.forEach( function(p) {
	let es = gdata[p.id][esprop] ?? {size:gedge_def.size};
	p.value = es.size;
    });
}



/* Set the node colors for the specified scheme and redraw the display. The 
   input scheme is a string (a key within the global graph data) */

function updateNodeColors(ncprop) {
    setNodeColors(ncprop);
    dispUpdate();
}



/* Set the edge colors for the specified scheme and redraw the display. The 
   input scheme is a string (a key within the global graph data) */

function updateEdgeColors(ecprop) {
    setEdgeColors(ecprop);
    dispUpdate();
}



/* Set the edge sizes for the specified scheme and redraw the display. The 
   input scheme is a string (a key within the global graph data) */

function updateEdgeSizes(esprop) {
    setEdgeSizes(esprop);
    dispUpdate();
}



/* This updates the display to center and highlight a specific node whose
   id (string) is provided as input */


function seleNode(nodeId) {
    setTransparent();
    setSolidNodes([nodeId]);
    dispUpdate();
    network.focus(nodeId, {animation: true});
    network.selectNodes([nodeId]);
}



/* This updates the display to center and highlight a specific edge whose
   id (string) is provided as input */

function seleEdge(edgeId) {
    var myEdges = edges.get(edgeId);
    //network.focus(myEdges.from, {animation: true});
    var uniqNodes = [ myEdges.from, myEdges.to ];
    setTransparent();
    setSolidNodes(uniqNodes);
    setSolidEdges([edgeId]);
    dispUpdate();
    network.setSelection( { nodes: uniqNodes, edges: [edgeId] }, { unselectAll: true, highlightEdges: false } );
    network.fit({ nodes: uniqNodes, animation: true });
}



/* utility function used to filter unique elements from an array */

function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;
}



/* This updates the display to center and highlight a cycle. The input is a
   list of edge id values */

function seleCycle(edgeIds) {
    var allNodes = [];
    var myEdges = edges.get(edgeIds);
    myEdges.forEach( function(edge) {	      
	allNodes.push( edge.from )
	allNodes.push( edge.to )
    });
    var uniqNodes = allNodes.filter(onlyUnique);
    setTransparent();
    setSolidNodes(uniqNodes);
    setSolidEdges(edgeIds);
    dispUpdate();
    network.setSelection( { nodes: uniqNodes, edges: undefined }, { unselectAll: true, highlightEdges: false } );
    network.fit({ nodes: uniqNodes, animation: true });
}



/* Create a list of node properties for all nodes contained within the
   gnodes global variable */

const nodeopts_default = [];
gnodes.forEach( function(node) {
    nodeopts_default.push({ id: node, label: node, opacity: 1,
			    color: { background: gnode_def.color,
				     border: "rgb(0,0,0)",
				     highlight: { background: gnode_def.color,
						  border: "rgb(0,0,0)" },
				     hover: { background: gnode_def.color,
					      border: "rgb(0,0,0)" } } })
});



/* Create a list of edge properties for all nodes contained within the
   gedges global variable */

const edgeopts_default = [];
gedges.forEach( function(edge) {
    let ligs = edge.split("~");
    edgeopts_default.push( { id: edge, from: ligs[0], to: ligs[1], color: { color: "rgb(0,0,0)", highlight: "rgb(0,0,0)", opacity: 1, inherit: false }, value: 1 } );
});



/* Copy the properties to nodeopts_current and edgeopts_current which is
   what the functions described above perform actions on. The nodeopts_default
   and edgeopts_default are backups of the original values for debugging
   purposes only */

var nodeopts_current = deepCopyFunction(nodeopts_default);
var edgeopts_current = deepCopyFunction(edgeopts_default);

// create an array with nodes
var nodes = new vis.DataSet(nodeopts_current);

// create an array with edges
var edges = new vis.DataSet(edgeopts_current);

// create a network
var container = document.getElementById("mynetwork");

var data = {
    nodes: nodes,
    edges: edges
};

var options = {
    //nodes: {shape: "dot";}
    edges: { scaling: { min: 3, max: 18,
			customScalingFunction:
			function (min,max,total,value) {
			    if (max === min) {
				return 0;
			    }
			    else {
				let scale = 1 / (max - min);
				return Math.max(0,(value - min)*scale);
			    }  }
		      }
	   }
};

var network = new vis.Network(container, data, options);


network.on( 'click', function(data) {
    if ( data.nodes.length == 0 && data.edges.length == 1 ) {
	//console.log(data.edges[0]);
	//console.log(edges.get(data.edges[0]));
	seleRow("row_" + data.edges[0]);
    }
    else if ( data.nodes.length == 1 ) {
	//console.log(data.nodes[0]);
	//console.log(nodes.get(data.nodes[0]));
	seleRow("row_" + data.nodes[0]);
    }
    //console.log(data.nodes,data.nodes.length,data.edges.length);
});

network.on( 'doubleClick', function(data) {
    if ( data.nodes.length == 0 && data.edges.length == 1 ) {
	//window.location.href = data.edges[0] + ".html";
	window.open(data.edges[0] + ".html",'_blank');
    }
});

setDefault();
dispUpdate();

