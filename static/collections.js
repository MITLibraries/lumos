// custom javascript

$(function() {
  createGraph();
});

function compare(a,b) {
  if (a.size < b.size)
    return 1;
  if (a.size > b.size)
    return -1;
  return 0;
}

function createGraph() {
  function getLegendRange() {
    r = [];
    for (k in legendDomain) {
      r.push(scale(legendDomain[k]));
    }
    return r;
  }

  var w = document.getElementById("display").offsetWidth;
  var lw = w * 2/3;
  var rw = w * 1/3;
  var h = lw * 0.37

  var currentSubject = {"name":"all_subjects", "locations":[]};
  var color = d3.scale.category20();
  var colls = JSON.parse(collections);

  var scale = d3.scale.linear()
    .domain([1, 5000, 50000, 500000, 1000000])
    .range([2, 20, 40, 60, 80]);
  var legendDomain = [1000000, 100000, 10000, 100];
  var legendRange = getLegendRange();

  var key = d3.select("#info")
    .append("svg")
    .attr("id", "key")
    .attr("width", rw)
    .attr("height", colls.length*25 + 40);

  var margin = 20;
  var padding = 6;
  var diameter = Math.min(lw, h);

  var lsvg = d3.select("#display")
    .append("svg")
    .attr("id", "mapcontainer")
    .attr("width", lw)
    .attr("height", h);

  var infoBox = d3.select("#display")
    .append("div")
    .attr("id", "infoBox")
    .attr("width", lw);

  var tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden")
    .style("color", "white")
    .style("padding", "8px")
    .style("background-color", "rgba(0, 0, 0, 0.8)")
    .style("border-radius", "6px")
    .style("font", "12px sans-serif")
    .style("line-height", "1.5")
    .text("tooltip");

  var map = d3.select("#mapcontainer")
    .append("image")
    .attr("xlink:href","/static/basemap_gray.svg")
    .attr("width", "100%")
    .attr("height", "100%");

  var tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden")
    .style("color", "white")
    .style("padding", "8px")
    .style("background-color", "rgba(0, 0, 0, 0.8)")
    .style("border-radius", "6px")
    .style("font", "12px sans-serif")
    .style("line-height", "1.5")
    .text("tooltip");

  d3.json('static/collections_data.json', function(error, data) {
    if (error) return console.error(error);

    var locations = data.children;
    locations = locations.sort(compare);

    d3.select("#infoBox")
      .append("foreignObject")
      .attr("x", 20)
      .attr("width", lw-20)
      .attr("height", 200)
      .append("xhtml:body")
      .attr("class", "mdText")
      .html(function() {
        textContent = "<p><strong>Totals</strong><br />";
        for (item in locations) {
          if (locations[item].size > 1) {
            textContent += locations[item].size + " items in " + locations[item].name + "<br />";
          } else {
            textContent += locations[item].size + " items in " + locations[item].name + "<br />";
          }
        }
        textContent += "</p>";
        return textContent;
      });

    var keyCircles = key.selectAll("circle")
      .data(colls)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("cx", 30)
      .attr("cy", function(d, i) {
        return 20 + i*24;
      })
      .style("fill", function(d) { 
        return color(d); 
      })
      .style("fill-opacity", "0.6")
      .on("mouseover", function(d, i) {
        d3.selectAll("p").remove();
        currentSubject.locations = [];

        circle.classed("faded_map_node", true);
        circle.classed("initial", false);

        circle.attr("r", function(e, j) {
          for (item in e.children) {
            if (d == e.children[item].name) {
              return scale(e.children[item].size);
            }
          }
        });

        circle.attr("fill", function() {
          return color(d);
        });

        circle.classed("active_map_node", function(e, j) {
          for (item in e.children) {
            if (d == e.children[item].name) {
              currentSubject.name = e.children[item].name;
              currentSubject.locations.push({"name":e.name, "size":e.children[item].size});
              currentSubject.locations.sort(compare);
              return true;
            }
          }
        });

        label.attr("y", function(e) {
          for (item in e.children) {
            if (d == e.children[item].name) {
              return e.y_offset * h + scale(e.children[item].size) + 8;
            }
          }
        });

        d3.select("#infoBox")
          .append("foreignObject")
          .attr("x", 20)
          .attr("width", lw-20)
          .attr("height", 200)
          .append("xhtml:body")
          .attr("class", "mdText")
          .html(function() {
            textContent = "<p><strong>" + d + "</strong><br />";
            for (item in currentSubject.locations) {
              if (currentSubject.locations[item].size > 1) {
                textContent += currentSubject.locations[item].size + " items in " + currentSubject.locations[item].name + "<br />";
              } else {
                textContent += currentSubject.locations[item].size + " item in " + currentSubject.locations[item].name + "<br />";
              }
            }
            textContent += "</p>";
            return textContent;
          });
      });        

    var keyText = key.selectAll("text")
      .data(colls)
      .enter()
      .append("text")
      .attr("x", 45)
      .attr("y", function(d, i) {
        return 26 + i*24;
      })
      .attr("class", "keyText")
      .text(function(d) {
        return d;
      });

    var circle = lsvg.selectAll("circle")
      .data(locations)
      .enter().append("circle")
      .attr("cx", function(d) {
        return d.x_offset * lw;
      })
      .attr("cy", function(d) {
        return d.y_offset * h;
      })
      .attr("r", function(d) {
        return scale(d.size);
      })
      .attr("class", "active_map_node initial")
      .on("mouseover", function(d) {
        tooltip.html(function() {
          for (item in d.children) {
            if (d.children[item].name == currentSubject.name) {
              if (d.children[item].size > 1) {
                return d.children[item].name + "<br />" + d.children[item].size + " items in " + d.name;
              } else {
                return d.children[item].name + "<br />" + d.children[item].size + " item in " + d.name;
              }
            }
          }
          return d.size + " items in " + d.name;
        });
        tooltip.style("visibility", "visible");
      })
      .on("mousemove", function() {
        return tooltip.style("top", (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");
      })
      .on("mouseout", function(){
        return tooltip.style("visibility", "hidden");
      });

    var legend = lsvg.selectAll("rect")
      .data(legendRange)
      .enter().append("circle")
      .attr("class", "initial")
      .attr("cx", 100)
      .attr("cy", function(d, i) {
        if (i == 0) {
          return 100;
        } else {
          return 100 + legendRange[0] - d;
        }
      })
      .attr("r", function(d) {
        return d;
      });

    var label = lsvg.selectAll("text")
      .data(locations)
      .enter().append("text")
      .attr("class", "legendText")
      .style("text-anchor", "middle")
      .attr("x", function(d) {
        return d.x_offset * lw;
      })
      .attr("y", function(d) {
        return d.y_offset * h + scale(d.size) + 8;
      })
      .text(function(d) {
        return d.short_name;
      });

    var legendText = lsvg.selectAll("line")
      .data(legendRange)
      .enter().append("text")
      .attr("class", "legendText")
      .style("text-anchor", "middle")
      .attr("x", 100)
      .attr("y", function(d, i) {
        if (i == 0) {
          return 100 - d - 2;
        } else {
          return 100 + legendRange[0] - (2 * d) - 2;
        }
      })
      .text(function(d, i) {
        return legendDomain[i];
      });
  });

}