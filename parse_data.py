import csv
import json
import time
import xlrd


def parse_lc_class_subject_key(key_file_csv):
	"""Parse external LC classification-to-subject file.

	Args:
		key_file_csv (str): Path to csv file to be parsed. Must be saved as Windows CSV format.

	Returns:
		list: List of LC call range and subject pairs, sorted in order from longest call range to shortest (this is important for later data processing steps).
	"""
	keys = []
	with open(key_file_csv, 'rb') as key_file_csv:
		key_file = key_file_csv.readlines()
		for row in key_file:
			new_row = row.strip('\r\n')
			new_row = new_row.split(',')
			new_row[0] = new_row[0].strip()
			keys.append(new_row)
	keys.sort(key=lambda key: len(key[0]), reverse=True)
	return keys


def add_subject_field(data_file_tsv, call_no_subject_keys):
	"""Compare data file to LC call range keys and generate new data set that includes subject for each item.

	Args:
		data_file_csv (str): Path to csv file to be parsed. Must be saved as TSV format.
		call_no_subject_keys (list): List of paired call number ranges and subject names.

	Returns:
		list: List representing the data, where each list item is one row from the original data set with an added subject string (column) at the end of each row.
	"""
	with open(data_file_tsv, 'rb') as old_data_tsv:
		old_data = csv.reader(old_data_tsv, delimiter="\t")
		new_data = []
		numRows = 0

		for row in old_data:
			numRows += 1
		old_data_tsv.seek(0)

		for i in range(numRows):
			data_row = old_data.next()
			call_no = data_row[4]

			for key_row in (kr for kr in keys if kr[0] == call_no[:len(kr[0])]):
				try:
					if data_row[6]:
						break
				except IndexError:
					data_row.append(key_row[1])

			new_data.append(data_row)
	return new_data


def write_to_tsv(content, new_file):
	"""Writes list content to a new tab-separated text file.

	Args:
		content (list): Content to be written to file.
		new_file (string): Path to new file to be written, including desired name of new file (with extension).
	"""
	with open(new_file, 'wb') as new_data_tsv:
		writer = csv.writer(new_data_tsv, delimiter="\t")
		writer.writerows(content)


def add_to_tsv(content, existing_file):
	"""Appends list content to an existing tab-separated text file.

	Args:
		content (list): Content to be written to file.
		existing_file (string): Path to file to append to.
	"""
	with open(existing_file, 'a') as data_tsv:
		writer = csv.writer(data_tsv, delimiter="\t")
		writer.writerows(content)


def write_to_json(content, file):
	"""Writes list content to a json file.

	Args:
		content (dict): Content to be written to file.
		file (string): Path to file to be written, including desired name of file (with extension).
	"""
	with open(file, 'wb') as json_file:
		json.dump(content, json_file, indent=4)


def clean_new_data(input_data):
	"""Several processes to clean up data after adding subject column. Specific actions include:

		Delete first row: The first row of column headings is not needed.

		Remove rows without subject: Some rows do not have call numbers, and consequently did not get given subject fields. These will not be represented in the final visualization.

		Combine locations: A few library locations are represented with multiple names (e.g., "Science Library" and "Humanities Library" both represent Hayden), so those are processed to ensure one name for each location.

		Separate HD from LSA: All off-campus collections are listed as LSA, which must be sorted out using a different column. This clarification is done.

		Rename locations: Certain locations need to be renamed to match location names in other data files in this application.

	Args:
		input_data(list): List representing data set.

	Returns:
		list: List representing cleaned data set.
	"""
	data = input_data
	RESULTS = []

	del data[0]
	for row in data:
		try:
			if row[6]:
				if row[0] == 'Hayden Reserves' or row[0] == 'Humanities Library' or row[0] == 'Science Library':
					row[0] = 'Hayden Library'
				elif row[0] == 'Rotch Visual Collections':
					row[0] = 'Rotch Library'
				elif row[0] == 'Library Storage Annex':
					if row[1] == 'Off Campus Collection':
						row[0] = 'Harvard Depository'
					else:
						row[0] = 'Annex'
				elif row[0] == 'Institute Archives':
					row[0] = 'IASC'
				RESULTS.append(row)
		except(IndexError):
			pass

	return RESULTS

def get_collections_by_location_json(input_data_file):
	"""Parses input TSV file to create a hierarchical data set of locations, with collections by subject at each location.

	Args:
		input_data_file (string): Path to data file in tab-separated format.

	Returns:
		dict: Dictionary with hierarchy of locations, with collection subjects (and their sizes at each location) as children.
	"""
	RESULTS = {'name': 'MIT Libraries', 'size': 0, 'children': []}
	with open(input_data_file, 'rb') as data_file:
		data = csv.reader(data_file, delimiter='\t')

		for row in data:
			location = row[0]
			subject = row[6]

			update_children(RESULTS['children'], location, 'name', 'size', {
				'name': location,
				'size': 1,
				'children': []
				})

			location_index = find_dict_index(RESULTS['children'], 'name', location)

			update_children(RESULTS['children'][location_index]['children'], subject, 'name', 'size', {
				'name': subject,
				'size': 1
				})			

			RESULTS['size'] += 1
	
	mapdata = xlrd.open_workbook('data/map_data.xlsx')
	mapsheet = mapdata.sheet_by_index(0)

	for item in RESULTS['children']:
		for rowx in range(1, mapsheet.nrows):
			if item['name'].startswith(str(mapsheet.cell_value(rowx, 0))):
				item['x_offset'] = mapsheet.cell_value(rowx, 1)
				item['y_offset'] = mapsheet.cell_value(rowx, 2)

	return RESULTS


def update_children(parent, child, search_key, update_key, content=None):
	"""Updates a child dict given a parent array, does not require the index of the child object to be known (is found using the search key). The specified update key value is incremented by one. If the child object does not exist (given the specified search key), it is added to the parent array and the update key is given an initial value of 1.

	Args:
		parent (array): The parent array containing the child dict to be updated.
		child (string): The value of the key:value pair that identifies the child dict to update.
		search_key (string): The key of the key:value pair that identifies the child dict to update.
		update_key (string): The key within the child dict whose value should be updated (incremented by 1)
		content (dict): If the child dict does not exist, the complete dict content to be appended to the parent array.
	"""
	try:
		index = find_dict_index(parent, search_key, child)
		parent[index][update_key] += 1
	except(ValueError):
		parent.append(content)

def find_dict_index(array, key, value):
	"""Finds the index of a dict containing a specified key:value pair within an array of dicts.

	Args:
		array (array): The array containing the specified dict.
		key (string): The key to search for in each dict in the array.
		value: The specified value for the stated dict key.

	Returns:
		int: The index of the dict containing the specified key:value pair.

	Raises:
		ValueError: If the specified key:value pair is not found within the dicts in the given array.
	"""
	for i, d in enumerate(array):
		if d[key] == value:
			return i
	raise ValueError


if __name__ == '__main__':
	# Parse subject keys
	print "Start: " + time.strftime('%I:%M:%S')
	keys = parse_lc_class_subject_key('data/lc_class_subject_key.csv')
	print "Finish parsing subject keys: " + time.strftime('%I:%M:%S')
	# Process on campus data
	on_campus_data = add_subject_field('data/collections_data/item_by_location_campus.txt', keys)
	print "Finish adding subject field to on campus data: " + time.strftime('%I:%M:%S')
	clean_on_campus_data = clean_new_data(on_campus_data)
	print "Finish cleaning on campus data: " + time.strftime('%I:%M:%S')
	# Process off campus data
	off_campus_data = add_subject_field('data/collections_data/item_by_location_off_campus.txt', keys)
	print "Finish adding subject field to off campus data: " + time.strftime('%I:%M:%S')
	clean_off_campus_data = clean_new_data(off_campus_data)
	print "Finish cleaning off campus data: " + time.strftime('%I:%M:%S')
	# Write both data sets to combined file
	write_to_tsv(clean_on_campus_data, 'data/collections_data/combined_item_by_location.txt')
	print "Finish writing on campus data to file: " + time.strftime('%I:%M:%S')
	add_to_tsv(clean_off_campus_data, 'data/collections_data/combined_item_by_location.txt')
	print "Finish writing off campus data to file: " + time.strftime('%I:%M:%S')
	# Write final data to JSON file
	write_to_json(get_collections_by_location_json('data/collections_data/combined_item_by_location.txt'), 'static/collections_data.json')
	print "Finish writing all data to JSON file: " + time.strftime('%I:%M:%S')