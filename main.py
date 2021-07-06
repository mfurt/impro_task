from pathlib import Path
from data_utils import read_file, write_tsv


def get_basic_results(data_sources):
    m_set = None
    d_set = None

    for data in data_sources:
        m_keys = [key for key in data if key.startswith('M')]
        d_keys = [key for key in data if key.startswith('D')]

        m_set = m_set & set(m_keys) if m_set else set(m_keys)
        d_set = d_set & set(d_keys) if d_set else set(d_keys)

    basic_results = {key: [] for key in sorted(d_set | m_set)}
    for data in data_sources:
        for key in d_set | m_set:
            basic_results[key].extend(data[key])

    return basic_results


def get_advanced_results(basic_results):
    d_keys = [key for key in basic_results if key.startswith('D')]
    d_keys = sorted(d_keys)

    m_keys = [key for key in basic_results if key.startswith('M')]
    m_keys = sorted(m_keys)

    ms_keys = [m_key.replace('M', 'MS') for m_key in m_keys]

    n_values = len(basic_results[d_keys[0]])
    variant_dict = {}

    for i in range(n_values):
        variant = tuple([basic_results[d_key][i] for d_key in d_keys])

        if variant not in variant_dict:
            variant_dict[variant] = {m_key: [basic_results[m_key][i]] for m_key in m_keys}
        else:
            for m_key in m_keys:
                variant_dict[variant][m_key] += [basic_results[m_key][i]]

    advanced_results = {key: [] for key in d_keys + ms_keys}

    for variant, m_dict in variant_dict.items():
        for d_key, d_val in zip(d_keys, variant):
            advanced_results[d_key].append(d_val)

        for m_key, m_values in m_dict.items():
            advanced_results[m_key.replace('M', 'MS')].append(sum(m_values))

    return advanced_results


EXT = 'json xml csv'.split()

files = []
for ext in EXT:
    files.extend(Path('data').glob(f'*.{ext}'))

errors = []
data_sources = []

for file in files:
    data, err = read_file(str(file))

    data_sources.append(data)
    errors.extend(err)

if errors:
    print('Обнаружены следующие ошибки:')
    for error in errors:
        print(error)

basic_results = get_basic_results(data_sources)
advanced_results = get_advanced_results(basic_results)

write_tsv(basic_results, './result/basic_results.tsv')
write_tsv(advanced_results, './result/advanced_results.tsv')