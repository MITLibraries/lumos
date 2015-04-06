import xlrd
import json

file = xlrd.open_workbook('data/staff vis hierarchy location-function-size.xlsx')
sheet = file.sheet_by_index(0)
n = 1


def get_data_by_location(functions):
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

	def add_to_children(parent, child):
		index = get_child_index(parent, child)
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

		if sheet.cell_type(rowx, 1) != 0:
			index = get_child_index(parent, location)
			parent = RESULTS['children'][index]
			location = sub_location

		if function in functions:
			add_to_children(parent, location)

	# print json.dumps(RESULTS, indent=4, sort_keys=True)
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
	global n
	n = 1

	def add_node(name, group_type):
		global n
		nodes.append({
			'name': function,
			'group type': group_type,
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

	for row in range(1, sheet.nrows):
		location = sheet.cell_value(row, 0)
		function = sheet.cell_value(row, 2)
		group_type = sheet.cell_value(row, 4)

		nodes[get_index(function, nodes)]['locations'].append(location)

	# TODO: Add links array to results.

	return RESULTS


# def get_data_by_function(functions):
# 	RESULTS = []

# 	def get_child_index(parent, child):
# 		try:
# 			print parent, child
# 			return find(parent, 'name', child)	
# 		except ValueError:
# 			add_child_level(parent, child)
# 			return find(parent, 'name', child)

# 	def add_child_level(parent, child):
# 		parent.append({
# 			'name': child,
# 			'size': 0,
# 			'locations': []
# 			})

# 	def add_to_children(parent, child):
# 		index = get_child_index(parent, child)
# 		parent[index]['locations'].append({
# 			'name': str(sheet.cell_value(rowx, 0)),
# 			'size': sheet.cell_value(rowx, 3)
# 			})
# 		parent[index]['size'] += sheet.cell_value(rowx, 3)

# 	for rowx in range(1, sheet.nrows):
# 		parent = RESULTS
# 		location = str(sheet.cell_value(rowx, 0))
# 		sub_location = str(sheet.cell_value(rowx, 1))
# 		function = str(sheet.cell_value(rowx, 2))

# 		if sheet.cell_type(rowx, 1) != 0:
# 			index = get_child_index(parent, function)
# 			parent = RESULTS[index]
# 			location = sub_location

# 		if function in functions:
# 			add_to_children(parent, location)

# 	# print json.dumps(RESULTS, indent=4, sort_keys=True)
# 	return RESULTS


print json.dumps(get_data_node_link(), indent=4, sort_keys=False)
# print json.dumps(get_data_by_function(["Access Services", "Curation and Preservation", "Access Services", "Information Technology and Digital Development"]), indent=4, sort_keys=True)
# print json.dumps(get_groups(), indent=4, sort_keys=True)
# print json.dumps(get_hierarchy(["Annex Services", "Curation and Preservation", "Access Services", "Information Technology and Digital Development"]), indent=4, sort_keys=True)