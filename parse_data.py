import csv


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


def add_subject_field(data_file_csv, call_no_subject_keys):
	"""Compare data file to LC call range keys and generate new data set that includes subject for each item.

	Args:
		data_file_csv (str): Path to csv file to be parsed. Must be saved as Windows CSV format.
		call_no_subject_keys (list): List of paired call number ranges and subject names.

	Returns:
		list: List representing the data, where each list item is one row from the original data set with an added subject string (column) at the end of each row.
	"""
	with open(data_file_csv, 'rb') as old_data_tsv:
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


def write_content(content, new_file):
	"""Writes list content to a new tab-separated text file.

	Args:
		content (list): Content to be written to file.
		new_file (string): Path to new file to be written, including desired name of new file (with extension).
	"""
	with open(new_file, 'wb') as new_data_tsv:
		writer = csv.writer(new_data_tsv, delimiter="\t")
		writer.writerows(content)


keys = parse_lc_class_subject_key('data_testing/lc_class_subject_key.csv')
data = add_subject_field('data_testing/item_by_location_campus.txt', keys)
write_content(data, 'data_testing/new_item_by_location_campus.txt')