import os
import shutil
from functools import reduce
from typing import Dict
from hestia_earth.utils.blank_node import get_node_value
import numpy as np
import pandas as pd

from . import CYCLE_AGGREGATION_KEYS

_COVARIANCE_ROOT_DIR = os.getenv('TMP_DIR', '/tmp')
_ID_COLUMN = 'id'


def _covariance_dir(): return os.path.join(_COVARIANCE_ROOT_DIR, 'covariance')


def init_covariance_files():
    remove_covariance_files()
    os.makedirs(_covariance_dir(), exist_ok=True)


def remove_covariance_files():
    if os.path.exists(_covariance_dir()):
        shutil.rmtree(_covariance_dir())


def _covariance_filepath(suffix: str):
    os.makedirs(_covariance_dir(), exist_ok=True)
    return os.path.join(_covariance_dir(), f"covariance-{suffix}.csv")


def _list_covariance_files():
    return [f for f in os.listdir(_covariance_dir()) if f != 'covariance.csv']


def _read_filepath(filepath: str): return pd.read_csv(filepath, index_col=_ID_COLUMN, na_values='')


def _read_file(suffix: str): return _read_filepath(_covariance_filepath(suffix))


def _group_covariance_data(group: dict, value: Dict[str, dict]) -> dict:
    group_key = value['term']['@id']
    group[group_key] = group.get(group_key) or {'term': value['term'], 'value': []}
    value = value.get('value')
    value is not None and group[group_key]['value'].extend(value if isinstance(value, list) else [value])
    return group


def _map_covariance_data(list_key: str, key: str, value: list):
    group_key = f"{list_key}.{key}"
    value = get_node_value(value, default=None) if len(value) > 0 else None
    is_0_practice = list_key == 'practices' and not value
    return ({} if is_0_practice else {group_key: value})


def _cycle_list_covariance_data(cycle: dict, list_key: str):
    blank_nodes = list(cycle.get(list_key, {}).values())
    data = reduce(_group_covariance_data, blank_nodes, {})
    return reduce(lambda prev, curr: prev | _map_covariance_data(list_key, curr, data[curr]), data.keys(), {})


def _cycle_covariance_data(cycle: dict):
    data = reduce(lambda prev, curr: prev | _cycle_list_covariance_data(cycle, curr), CYCLE_AGGREGATION_KEYS, {})
    return {_ID_COLUMN: cycle.get('cycle_ids')[0]} | data


def add_covariance_cycles(cycles: list, suffix: str):
    records = list(map(_cycle_covariance_data, cycles))
    df = pd.DataFrame(records).set_index(_ID_COLUMN).fillna('')
    filepath = _covariance_filepath(suffix)
    # combine new data with existing data
    df = pd.concat([df, _read_file(suffix)]) if os.path.exists(filepath) else df
    df.to_csv(filepath, na_rep='')


def _format_covariance_value(value):
    return None if pd.isna(value) else value


def _format_covariance_matrix(values):
    # replace NaN values with None, so it is set to `null` in JSON
    return [
        list(map(_format_covariance_value, values))
        for values in np.tril(values)
    ]


def generate_covariance_cycles(suffix: str):
    df = _read_file(suffix).sort_index(axis=1)
    matrix = df.cov().values
    return {'covarianceMatrixIds': list(df.columns), 'covarianceMatrix': _format_covariance_matrix(matrix)}


def _read_covariance_subcountry_file(weights: dict):
    def read_file(filename: str):
        filepath = os.path.join(_covariance_dir(), filename)
        df = _read_filepath(filepath)
        nb_rows = df.shape[0]
        matrix = filename.replace('covariance-', '').replace('.csv', '')
        weight_values = next((v for k, v in weights.items() if matrix in k), next(iter(weights.values())))
        weight = weight_values['weight'] / nb_rows
        df['weight'] = weight
        return df

    return read_file


def generate_covariance_country(weights: dict):
    files = _list_covariance_files()
    frames = list(map(_read_covariance_subcountry_file(weights), files))
    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]

    weights = df['weight']
    data = df.drop(columns=['weight'])
    # Compute weighted covariance
    matrix = np.cov(data.T, aweights=weights)

    return {'covarianceMatrixIds': list(data.columns), 'covarianceMatrix': _format_covariance_matrix(matrix)}
