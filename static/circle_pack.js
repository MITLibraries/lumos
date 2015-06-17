// custom javascript

$(function() {
  createGraph();
});

function createGraph() {
	var w = document.getElementById("display").offsetWidth;
	var lw = w * 2/3;
	var rw = w * 1/3;
	var h = document.getElementById("display").offsetHeight - 120;

	var color = d3.scale.category20();

	var key = d3.select("#info")
		.append("svg")
		.attr("id", "key")
		.attr("width", rw)
		.attr("height", JSON.parse(key_text).length*25 + 40);

	var margin = 20;
	var padding = 6;
	var diameter = Math.min(lw, h);

	var lsvg = d3.select("#display")
		.append("svg")
		.attr("width", lw)
		.attr("height", h)
		.attr("float", "left")
		.append("g")
		.attr("transform", "translate(" + lw / 2 + "," + h / 2 + ")");

	var pack = d3.layout.pack()
		.padding(padding)
		.size([diameter - margin, diameter - margin])
		.value(function(d) { return d.size; });

	var tooltip = d3.select("body")
		.append("div")
		.style("position", "absolute")
		.style("z-index", "10")
		.style("visibility", "hidden")
		.style("color", "white")
		.style("padding", "8px")
		// .style("background-color", "navy")
		.style("background-color", "rgba(0, 0, 0, 0.8)")
		.style("border-radius", "6px")
		.style("font", "12px sans-serif")
		.style("line-height", "1.5")
		.text("tooltip");

	d3.selection.prototype.moveToFront = function() {
		return this.each(function(){
			this.parentNode.appendChild(this);
		});
	};

	d3.selection.prototype.moveToBack = function() { 
		return this.each(function() { 
			var firstChild = this.parentNode.firstChild; 
			if (firstChild) { 
				this.parentNode.insertBefore(this, firstChild); 
			} 
		}); 
	};

	d3.json("/data/" + level, function(error, root) {
		if (error) return console.error(error);

		var focus = root;
		var nodes = pack.nodes(root);
		var view;

		var keyCircles = key.selectAll("circle")
			.data(JSON.parse(key_text))
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
			.on("mouseover", function(d, i) {
				circle.classed("faded_node", function(e, j) {
					if (d != e.name || !circle.classed("node-root")) {
						return true;
					}
					else {return false}
				});
				circle.classed("active_node", function(e, j) {
					if (d == e.name) {
						return true;
					}
					else {return false}
				});
			})
			.on("mouseout", function(d, i) {
        		circle.classed("active_node", true);
        		circle.classed("faded_node", false);
      		});

		  var keyText = key.selectAll("text")
			.data(JSON.parse(key_text))
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
			.data(nodes)
			.enter().append("circle")
			.attr("class", function(d) { 
				return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; 
			})
			.style("fill", function(d) {
				return !d.children ? color(d.name) : "white"; 
			})
			.style("stroke", function(d) {
				return d.children ? "black" : null;
			})
			.on("click", function(d) { 
				if (focus !== d) zoom(d), d3.event.stopPropagation(); 
			})
			.on("mouseover", function(d) {
				if (d3.select(this).classed("node--leaf")) {
					tooltip.html(function() {
						if (d.size > 1) {
							return d.name + "<br />" + d.size + " people in " + d.parent.name;
						}
						else {
							return d.name + "<br />" + d.size + " person in " + d.parent.name;
						}
					});
					tooltip.style("visibility", "visible");
				}
			})
			.on("mousemove", function() {
				return tooltip.style("top", (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");
				})
			.on("mouseout", function(){
				return tooltip.style("visibility", "hidden");
			});

		var text = lsvg.selectAll("text")
			.data(nodes)
			.enter().append("text")
			.attr("transform", function(d) {
				return "translate(" + 0 + "," + 0 + ")";
			})
			.attr("text-anchor", "middle")
			.attr("class", "label")
			.style("display", function(d) {
				return d.parent === root ? null : !d.children ? "none" : null;
			})
			.text(function(d) {
				return d.name;
			});

		var node = lsvg.selectAll("circle, text");

		d3.select("body")
			.on("click", function() { zoom(root); });

		zoomTo([root.x, root.y, root.r * 2 + margin]);

		function zoom(d) {
			var focus0 = focus; focus = d;

			var transition = d3.transition()
				.duration(d3.event.altKey ? 7500 : 750)
				.tween("zoom", function(d) {
					var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
					return function(t) { zoomTo(i(t)); };
				});

			transition.selectAll("text")
				.filter(function(d) { return this === focus || this.style.display === "inline"; })
				.style("fill-opacity", function(d) { return this === focus ? 1 : 0; })
				.each("start", function(d) { if (this === focus) this.style.display = "inline"; })
				.each("end", function(d) { if (this !== focus) this.style.display = "none"; });
		}

		function zoomTo(v) {
			var k = diameter / v[2]; view = v;
			node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
			circle.attr("r", function(d) { return d.r * k; });
			text.attr("transform", function(d) {
				return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1] - d.r - padding + 10) * k + ")";
			});
		}
	});

	d3.select(self.frameElement).style("height", diameter + "px");
}




