/**
 * Created by oliverbecher on 13/04/2017.
 */
let barChart = function (){

    function init(){

    }

    function draw(data){
        var contrastC = ['#fdfdfd', '#1d1d1d', '#ebce2b', '#702c8c', '#db6917', '#96cde6', '#ba1c30', '#c0bd7f', '#7f7e80', '#5fa641', '#d485b2', '#4277b6', '#df8461', '#463397', '#e1a11a', '#91218c', '#e8e948', '#7e1510', '#92ae31', '#6f340d', '#d32b1e', '#2b3514'];
        var format = d3.time.format("%Y-%m-%d");

        data.forEach(function(d) {
            d.date = format.parse(d.date);
            d.value = +d.value;
        });

        var margin = {top: 20, right: 30, bottom: 30, left: 40},
            width = 960 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var svg = d3.select(tag)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


        colorMap = new Object();
        for (i in data) {
            colorMap[data[i].key] = contrastC[i%contrastC.length];
        }
        var dataset = d3.layout.stack()(headerNames.map(function(annotations) {
            return data.map(function(d) {
                return {x: d.Date, y: +d[annotations], z: annotations};
            });
        }));
        for (d in data){
            dataset[d].annot = dataset[d][0].z;
        }
        var x = d3.scale.ordinal()
            .domain(dataset[0].map(function(d) { return d.x; }))
            .rangeRoundBands([10, width-10], 0.02);

        var y = d3.scale.linear()
            .domain([0, d3.max(dataset, function(d) {  return d3.max(d, function(d) { return d.y0 + d.y; });  })])
            .range([height, 0]);


        // Define and draw axes
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .ticks(5)
            .tickSize(-width, 0, 0)
            .tickFormat( function(d) { return d } );

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickFormat(d3.time.format("%b-%y"));

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);


        // Create groups for each series, rects for each segment
        var groups = svg.selectAll("g.cost")
            .data(dataset)
            .enter().append("g")
            .attr("class", "cost")
            .style("fill", function(d, i) {
                if (d.annot) {
                    return colorMap[d.annot]; }
                else {
                    return '#000000';}
            });

        var rect = groups.selectAll("rect")
            .data(function(d) { return d; })
            .enter()
            .append("rect")
            .attr("x", function(d) { return x(d.x); })
            .attr("y", function(d) { return y(d.y0 + d.y); })
            .attr("height", function(d) { return y(d.y0) - y(d.y0 + d.y); })
            .attr("width", x.rangeBand())
            .on("mouseover", function() { tooltip.style("display", null); })
            .on("mouseout", function() { tooltip.style("display", "none"); })
            .on("mousemove", function(d) {
                var xPosition = d3.mouse(this)[0] - 15;
                var yPosition = d3.mouse(this)[1] - 25;
                tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
                //console.log(d)
                tooltip.select("text").text(d.z, d.y);
            })
            .on("click", function(d) {
                if (focus === 1) {
                    focus = 0;
                    d3.selectAll("rect").style("fill", function(d, i) {
                        if (d.z) {
                            return colorMap[d.z]; }
                        else {
                            return '#000000';}});
                } else {
                    focus = 1;
                    var code = d.z;
                    d3.selectAll("rect").style("fill", function(d, i) {
                        if (d.z === code) {
                            return colorMap[d.z]; }
                        else {
                            return '#6c6c6c';}});
                }
            });

        // Prep the tooltip bits, initial display is hidden
        var tooltip = svg.append("g")
            .attr("class", "tooltip")
            .style("display", "none");

        tooltip.append("text")
            .attr("x", 15)
            .attr("dy", "1.2em")
            .style("text-anchor", "middle")
            .attr("font-size", "12px")
            .attr("font-weight", "bold");
    }
    }

}
var callbackError;
var callbackData;
var headerNames;
var colorMap;
var focus = 0;


function init_graph(data, tag) {



d3.csv("analysis_adds13291.csv", type, function(error, data) {
    headerNames = d3.keys(data[0]).slice(1);
    callbackError = error;
    callbackData = data;
    init_graph(callbackData, "#adds");
});

d3.csv("analysis_rems13291.csv", type, function(error, data) {
    headerNames = d3.keys(data[0]).slice(1);
    callbackError = error;
    callbackData = data;
    init_graph(callbackData, "#rems");
});


