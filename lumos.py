from flask import Flask, render_template, jsonify, request
from data_vis import get_data_by_location, get_groups, get_data_node_link, get_subjects_list
from parse_data import get_collections_by_location_json
import json

app = Flask(__name__)
app.config.from_object('default_config')
app.config.from_envvar('LUMOS_SETTINGS', silent=True)

levels = ['Directorate', 'Department', 'Unit', 'Group']

@app.route("/")
@app.route("/<level>")
def index(level="Directorate"):
	display_functions = get_groups(level)
	return render_template("index.html", functions=display_functions, level=level, levels=levels)

@app.route("/collections")
def collections():
	subjects = get_subjects_list()
	return render_template("collections.html", subjects=subjects)
	
@app.route("/map")
@app.route("/map/<level>")
def map(level="Directorate"):
	display_functions = get_groups(level)
	return render_template("map.html", functions=display_functions, level=level, levels=levels)

@app.route("/matrix")
def matrix():
	return render_template("matrix.html")

@app.route("/data")
@app.route("/data/<level>")
def data(level="Directorate"):
	selected_groups = get_groups(level)
	return jsonify(get_data_by_location(selected_groups, True))

@app.route("/matrix_data")
def matrix_data():
	return jsonify(get_data_node_link())

@app.route("/map_data")
@app.route("/map_data/<level>")
def map_data(level="Directorate"):
	selected_groups = get_groups(level)
	return jsonify(get_data_by_location(selected_groups, False))

@app.route("/collections_data")
def collections_data():
	return jsonify(get_collections_by_location_json('data_testing/combined_item_by_location.txt'))
	
if __name__ == "__main__":
	app.run(debug=True)