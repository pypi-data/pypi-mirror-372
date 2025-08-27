
google.charts.load('current', {'packages':['corechart']}); 

function tschart( divid, title, ymin, ymax, labels, colors, xlabel, dmat ) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', xlabel);
    data.addColumn('number', labels[0]);
    data.addColumn({type:'number', role:'interval'});
    data.addColumn({type:'number', role:'interval'});
    data.addColumn('number', labels[1]);
    data.addColumn({type:'number', role:'interval'});
    data.addColumn({type:'number', role:'interval'});
    data.addColumn('number', labels[2]);
    data.addColumn({type:'number', role:'interval'});
    data.addColumn({type:'number', role:'interval'});
    data.addRows(dmat);
    // to show the title, remove "titlePosition: 'none'," and set "top:50" in the chartArea
    var options = {
        title: title, titlePosition: 'none',
        hAxis: { title: xlabel, minValue: 0, maxValue: 1, titleTextStyle: { italic: false }, viewWindow: { min: 0, max: 1.05 } },
        vAxis: { viewWindow: { min: ymin, max: ymax } },
        intervals: { style: 'area', barWidth: 0.2, lineWidth: 2 },
        legend: { position: "bottom" },
        lineWidth: 2, pointSize: 5, height: 400, chartArea: {left:55,top:10,bottom:50, right:10, width:"100%",height:"100%"},
        explorer: { maxZoomOut: 1, keepInBounds: true },
        series: {
	    0: { color: colors[0], lineDashStyle: [5,5],
		 lineWidth: 4, pointSize: 0,
		 intervals: { style: 'area' }},
	    1: { color: colors[1] },
	    2: { color: colors[2] }
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById(divid));
    chart.draw(data, options);
}


function tschart1( divid, title, ymin, ymax, labels, colors, xlabel, dmat ) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', xlabel);
    data.addColumn('number', labels[0]);
    data.addColumn({type:'number', role:'interval'});
    data.addColumn({type:'number', role:'interval'});
    data.addRows(dmat);
    // to show the title, remove "titlePosition: 'none'," and set "top:50" in the chartArea
    var options = {
        title: title, titlePosition: 'none',
        hAxis: { title: xlabel, minValue: 0, maxValue: 1, titleTextStyle: { italic: false }, viewWindow: { min: 0, max: 1.05 } },
        vAxis: { viewWindow: { min: ymin, max: ymax } },
        intervals: { style: 'area', barWidth: 0.2, lineWidth: 2 },
        legend: { position: "bottom" },
        lineWidth: 2, pointSize: 5, height: 400, chartArea: {left:55,top:10,bottom:50, right:10, width:"100%",height:"100%"},
        explorer: { maxZoomOut: 1, keepInBounds: true },
        series: {
	    0: { color: colors[0] }
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById(divid));
    chart.draw(data, options);
}


function chichart( divid, colors, xmin, xmax, ymin, ymax, omat, fmat ) {
    let xlabel = 'Free Energy (kcal/mol)';
    let title = 'Objective Function';
    //let colors = [ '#000000', '#FF0000', '#006CFF' ];
    var odata = new google.visualization.DataTable();
    odata.addColumn('number', xlabel);
    odata.addColumn('number', 'Obs.');
    odata.addRows(omat);
    var fdata = new google.visualization.DataTable();
    fdata.addColumn('number', xlabel);
    fdata.addColumn('number', 'Quad. fit');
    fdata.addColumn('number', 'Cubic fit');
    fdata.addRows(fmat);
    var data = google.visualization.data.join(odata, fdata, 'full', [[0, 0]], [1], [1,2]);
    
    // to show the title, remove "titlePosition: 'none'," and set "top:50" in the chartArea
    var options = {
        title: title, titlePosition: 'none',
        hAxis: { title: xlabel, viewWindow: { min: xmin, max: xmax },
		 titleTextStyle: { italic: false }},
	vAxis: { viewWindow: { min: ymin, max: ymax } },
        legend: { position: "bottom" },
        lineWidth: 2, pointSize: 0, height: 400, chartArea: {left:55,top:10,bottom:50, right:10, width:"100%",height:"100%"},
        explorer: { maxZoomOut: 1, keepInBounds: true },
        series: {
	    0: { color: colors[0], lineWidth: 0, pointSize: 5 },
	    1: { color: colors[1], curveType: 'function' },
	    2: { color: colors[2], curveType: 'function', lineDashStyle: [5,5] }
        }
    };
    var chart = new google.visualization.LineChart(document.getElementById(divid));
    chart.draw(data, options);
}




function dvdlchart2( divid, colors, xmin, xmax, ymin, ymax, omat, fmat ) {
    let xlabel = 'Lambda';
    let title = 'DVDL';
    //let colors = [ '#000000', '#FF0000', '#006CFF' ];
    var odata = new google.visualization.DataTable();
    odata.addColumn('number', xlabel);
    odata.addColumn('number', 'Obs. Mean');
    odata.addRows(omat);
    var fdata = new google.visualization.DataTable();
    fdata.addColumn('number', xlabel);
    fdata.addColumn('number', 'Natural');
    fdata.addColumn('number', 'Clamped');
    //fdata.addColumn('number', 'USub');
    fdata.addRows(fmat);
    var data = google.visualization.data.join(odata, fdata, 'full', [[0,0]], [1], [1,2]);
    
    // to show the title, remove "titlePosition: 'none'," and set "top:50" in the chartArea
    var options = {
        title: title, titlePosition: 'none',
        hAxis: { title: xlabel, viewWindow: { min: xmin, max: xmax },
		 titleTextStyle: { italic: false }},
	vAxis: { viewWindow: { min: ymin, max: ymax } },
        legend: { position: "bottom" },
        lineWidth: 2, pointSize: 0, height: 400, chartArea: {left:55,top:10,bottom:50, right:10, width:"100%",height:"100%"},
        explorer: { maxZoomOut: 1, keepInBounds: true },
        series: {
	    0: { color: colors[0], lineWidth: 2, pointSize: 5 },
	    1: { color: colors[1], curveType: 'function' },
	    2: { color: colors[2], curveType: 'function' },
	    //3: { color: colors[3], curveType: 'function' },
        }
    };
    var chart = new google.visualization.LineChart(document.getElementById(divid));
    chart.draw(data, options);
}


function dvdlchart3( divid, colors, xmin, xmax, ymin, ymax, omat, fmat ) {
    let xlabel = 'Lambda';
    let title = 'DVDL';
    //let colors = [ '#000000', '#FF0000', '#006CFF' ];
    var odata = new google.visualization.DataTable();
    odata.addColumn('number', xlabel);
    odata.addColumn('number', 'Obs. Mean');
    odata.addRows(omat);
    var fdata = new google.visualization.DataTable();
    fdata.addColumn('number', xlabel);
    fdata.addColumn('number', 'Natural');
    fdata.addColumn('number', 'Clamped');
    fdata.addColumn('number', 'USub');
    fdata.addRows(fmat);
    var data = google.visualization.data.join(odata, fdata, 'full', [[0,0,0]], [1], [1,2,3]);
    
    // to show the title, remove "titlePosition: 'none'," and set "top:50" in the chartArea
    var options = {
        title: title, titlePosition: 'none',
        hAxis: { title: xlabel, viewWindow: { min: xmin, max: xmax },
		 titleTextStyle: { italic: false }},
	vAxis: { viewWindow: { min: ymin, max: ymax } },
        legend: { position: "bottom" },
        lineWidth: 2, pointSize: 0, height: 400, chartArea: {left:55,top:10,bottom:50, right:10, width:"100%",height:"100%"},
        explorer: { maxZoomOut: 1, keepInBounds: true },
        series: {
	    0: { color: colors[0], lineWidth: 2, pointSize: 5 },
	    1: { color: colors[1], curveType: 'function' },
	    2: { color: colors[2], curveType: 'function' },
	    3: { color: colors[3], curveType: 'function' },
        }
    };
    var chart = new google.visualization.LineChart(document.getElementById(divid));
    chart.draw(data, options);
}


function multidvdlchart( divid, colors, xmin, xmax, ymin, ymax, fmat, labels ) {
    var title="Title";
    var data = new google.visualization.DataTable();
    for ( let i=0; i<labels.length; i++ ) {
        data.addColumn('number', labels[i]);
    };
    data.addRows(fmat);

    var myseries = new Object();
    for ( let i=0; i<labels.length-1; i++ ) {
	myseries[i] = { color: colors[i], lineWidth: 2 };
    };
    
    // to show the title, remove "titlePosition: 'none'," and set "top:50" in the chartArea
    var options = {
        title: title, titlePosition: 'none',
        hAxis: { title: labels[0], viewWindow: { min: xmin, max: xmax },
		 titleTextStyle: { italic: false }},
	vAxis: { viewWindow: { min: ymin, max: ymax } },
        legend: { position: "bottom" },
        lineWidth: 2, pointSize: 0, height: 400, chartArea: {left:55,top:10,bottom:50, right:10, width:"100%",height:"100%"},
        explorer: { maxZoomOut: 1, keepInBounds: true },
        series: myseries
    };

    var chart = new google.visualization.LineChart(document.getElementById(divid));

    chart.draw(data, options);

    function showHideSeries () {
        var sel = chart.getSelection();
        // if selection length is 0, we deselected an element
        if (sel.length > 0) {
            // if row is undefined, we clicked on the legend
            if (sel[0].row == null) {
                var col = sel[0].column;
                if (options.series[col-1].lineWidth > 0) {
		    options.series[col-1].lineWidth = 0;
                }
		else {
		    options.series[col-1].lineWidth = 2;
                }
		chart.draw(data,options);
            }
	}
    }	
    google.visualization.events.addListener(chart, 'select', showHideSeries);   
}
