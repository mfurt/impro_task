import csv
from xml.etree import ElementTree
import json

def read_csv(filepath):
    reader = csv.reader(open(filepath))
    header = next(reader)

    data = {key: [] for key in header}

    for data_line in reader:
        for key, data_item in zip(header, data_line):
            data[key].append(data_item)

    return data


def read_xml(filepath):
    tree = ElementTree.parse(filepath)
    root = tree.getroot()

    objects = root.find('objects')

    data = {}
    for obj in objects.findall('object'):
        name = obj.attrib['name']
        data[name] = []

        for val in obj.findall('value'):
            data[name].append(val.text)

    return data


def read_json(filepath):
    json_data = json.load(open(filepath))
    fields = json_data['fields']

    data = {}
    for field in fields:
        for key, value in field.items():
            if key not in data:
                data[key] = []

            data[key].append(value)
    return data


def process_and_check_data(data):
    errors = []

    mkeys = [key for key in data if key.startswith('M')]

    for key in mkeys:
        for i, value in enumerate(data[key]):
            if isinstance(value, int):
                continue

            if isinstance(value, str) and value.isdigit():
                data[key][i] = int(value)
                continue

            data[key][i] = 0  # Заменяем на ноль, чтобы можно было считать суммы
            errors.append((key, i, value))

    return data, errors


def read_file(filepath):
    errors = []
    if filepath.endswith('.xml'):
        data = read_xml(filepath)

    elif filepath.endswith('.csv'):
        data = read_csv(filepath)

    elif filepath.endswith('.json'):
        data = read_json(filepath)

    else:
        data = {}
        errors.append(f'Unknown data format for {filepath}')

    data, data_errors = process_and_check_data(data)

    for data_error in data_errors:
        key, i, value = data_error
        errors.append(f'{filepath}: ключ {key}, строка {i + 1}, значение {value}')

    return data, errors


def write_tsv(data, filename):
    keys = list(data)

    tsv_data = [keys]
    n_values = len(data[keys[0]])

    for i in range(n_values):
        data_line = [data[key][i] for key in keys]
        tsv_data.append(data_line)

    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(tsv_data)
