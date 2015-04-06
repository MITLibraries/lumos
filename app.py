from flask import Flask, render_template, jsonify, request
from wtforms import Form, BooleanField
from data_vis import get_data_by_location, get_groups
import json

app = Flask(__name__)
app.config.from_object('config')

class CheckboxForm(Form):
	choices = BooleanField()

all_functions = get_groups()
display_functions = []
levels = ['Directorate', 'Department', 'Unit', 'Group']

@app.route("/", methods=['GET'])
@app.route("/<level>")
def index(level=None):
	global display_functions
	if level == None:
		display_functions = all_functions
	else:
		display_functions = get_groups(level)
		# print display_functions
	return render_template("index.html", level=display_functions, levels=levels)

@app.route("/data", methods=['GET','POST'])
def data():
	selected_groups = display_functions
	if request.method == 'POST':
		selected_groups = request.form.getlist("functions")
		print selected_groups
	return jsonify(get_data_by_location(selected_groups))

if __name__ == "__main__":
	app.run(debug=True)
