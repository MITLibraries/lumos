import xlrd
import json

file = xlrd.open_workbook('data/staff vis hierarchy location-function-size.xlsx')
sheet = file.sheet_by_index(0)

def get_hierarchy(functions):
	RESULTS = {'children': []}

	def get_child_index(parent, child):
		try:
			return find(parent['children'], 'name', child)	
		except ValueError:
			add_child_level(parent, child)
			return find(parent['children'], 'name', child)

	def add_to_children(parent, child):
		index = get_child_index(parent, child)
		parent['children'][index]['children'].append({
			'name': str(sheet.cell_value(rowx, 2)),
			'size': sheet.cell_value(rowx, 3)
			})

	def add_child_level(parent, child):
		parent['children'].append({
			'name': child,
			'children': []
			})

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


# print json.dumps(get_groups(), indent=4, sort_keys=True)
# print json.dumps(get_hierarchy(["Annex Services", "Curation and Preservation", "Access Services", "Information Technology and Digital Development"]), indent=4, sort_keys=True)