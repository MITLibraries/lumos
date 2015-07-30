import xlrd
import json
import csv

datafile = xlrd.open_workbook('data/staff vis hierarchy location-function-size.xlsx')
sheet = datafile.sheet_by_index(0)
mapdata = xlrd.open_workbook('data/map_data.xlsx')
mapsheet = mapdata.sheet_by_index(0)
n = 1

def get_data_by_location(functions, subloc):
	RESULTS = {'name': 'MIT Libraries', 'size': 0, 'children': []}

	def get_child_index(parent, child):
		try:
			return find(parent['children'], 'name', child)	
		except ValueError:
			add_child_level(parent, child)
			return find(parent['children'], 'name', child)

	def add_child_level(parent, child):
		parent['children'].append({
			'name': child,
			'size': 0,
			'children': []
			})

	def add_to_children(parent, child, function):
		index = get_child_index(parent, child)
		for item in parent['children'][index]['children']:
			if function == item['name']:
				item['size'] += sheet.cell_value(rowx, 3)
				parent['children'][index]['size'] += sheet.cell_value(rowx, 3)
				return True
		parent['children'][index]['children'].append({
			'name': str(sheet.cell_value(rowx, 2)),
			'size': sheet.cell_value(rowx, 3)
			})
		parent['children'][index]['size'] += sheet.cell_value(rowx, 3)

	for rowx in range(1, sheet.nrows):
		parent = RESULTS
		location = str(sheet.cell_value(rowx, 0))
		sub_location = str(sheet.cell_value(rowx, 1))
		function = str(sheet.cell_value(rowx, 2))

		if subloc == True:
			if sheet.cell_type(rowx, 1) != 0:
				index = get_child_index(parent, location)
				parent = RESULTS['children'][index]
				location = sub_location
			if function in functions:
				add_to_children(parent, location, function)
		else:
			if function in functions:
				add_to_children(parent, location, function)

	for item in RESULTS['children']:
		for rowx in range(1, mapsheet.nrows):
			if item['name'] == str(mapsheet.cell_value(rowx, 0)):
				item['x_offset'] = mapsheet.cell_value(rowx, 1)
				item['y_offset'] = mapsheet.cell_value(rowx, 2)

	return RESULTS

def find(array, key, value):
    for i, d in enumerate(array):
        if d[key] == value:
        	return i
    raise ValueError

def get_groups(group_type=None):
	RESULTS = []

	for rowx in range(1, sheet.nrows):
		function = str(sheet.cell_value(rowx, 2))
		function_type = str(sheet.cell_value(rowx, 4))

		if function not in RESULTS:
			if group_type == None:
				RESULTS.append(function)
			else:
				if function_type == group_type:
					RESULTS.append(function)

	return RESULTS

def get_data_node_link():
	RESULTS = {"nodes": [], "links": []}
	nodes = RESULTS['nodes']
	links = RESULTS['links']
	global n
	n = 0

	def add_node(name, group_type):
		global n
		nodes.append({
			'name': function,
			'group_type': group_type,
			'sort_key': n,
			'locations': []
		})
		n += 1

	def get_index(function, array):
		try:
			return find(array, 'name', function)
		except ValueError:
			add_node(function, group_type)
			return find(array, 'name', function)

	def find_link(array, source, target):
		for i, d in enumerate(array):
			if d['source'] == source and d['target'] == target:
				return i
		raise ValueError

	def add_to_links(array, source, target):
		try:
			array[find_link(array, source, target)]['value'] += 1
		except ValueError:
			array.append({
				'source': source,
				'target': target,
				'value': 1
				})

	for row in range(1, sheet.nrows):
		location = sheet.cell_value(row, 0)
		function = sheet.cell_value(row, 2)
		group_type = sheet.cell_value(row, 4)

		if location not in nodes[get_index(function, nodes)]['locations']:
			nodes[get_index(function, nodes)]['locations'].append(location)

	# Add links array to results.
	for node1 in nodes:
		node1_key = node1['sort_key']
		for node1_location in node1['locations']:
			for node2 in nodes[node1_key+1:]:
				node2_key = node2['sort_key']
				if node1_location in node2['locations']:
					add_to_links(links, node1_key, node2_key)

	return RESULTS

def get_subjects_list():
	RESULTS = []
	with open('data/lc_class_subject_key.csv', 'rb') as data_file:
		data = csv.reader(data_file)
		for row in data:
			if row[1] in RESULTS:
				pass
			else:
				RESULTS.append(str(row[1]))
	return sorted(RESULTS)