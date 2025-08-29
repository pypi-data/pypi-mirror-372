import os
from unittest.mock import patch

from tests.utils import fixtures_path
from hestia_earth.aggregation.utils.covariance import (
    add_covariance_cycles,
    init_covariance_files,
    remove_covariance_files,
    generate_covariance_cycles,
    generate_covariance_country
)

class_path = 'hestia_earth.aggregation.utils.covariance'
fixtures_folder = os.path.join(fixtures_path, 'utils', 'covariance')


def test_generate_covariance_cycles():
    init_covariance_files()

    cycles = [
        {
            'cycle_ids': ['cycle-1'],
            'inputs': {
                'ureaKgN': {
                    'term': {'@id': 'ureaKgN', '@type': 'Term'},
                    'value': 10
                },
                'pesticideUnspecifiedAi': {
                    'term': {'@id': 'pesticideUnspecifiedAi', '@type': 'Term'},
                    'value': 20
                }
            },
            'products': {
                'oilPalmFruit': {
                    'term': {'@id': 'oilPalmFruit', '@type': 'Term'},
                    'value': 30
                }
            }
        },
        {
            'cycle_ids': ['cycle-2'],
            'inputs': {
                'ureaKgN': {
                    'term': {'@id': 'ureaKgN', '@type': 'Term'},
                    'value': 30
                }
            },
            'products': {
                'oilPalmFruit': {
                    'term': {'@id': 'oilPalmFruit', '@type': 'Term'},
                    'value': 60
                }
            }
        }
    ]
    add_covariance_cycles(cycles, suffix='')

    data = generate_covariance_cycles(suffix='')
    assert data['covarianceMatrixIds'] == [
        'inputs.pesticideUnspecifiedAi',
        'inputs.ureaKgN',
        'products.oilPalmFruit'
    ]
    assert data['covarianceMatrix'] == [
        [None, 0.0, 0.0],
        [None, 200.0, 0.0],
        [None, 300.0, 450.0]
    ]

    remove_covariance_files()


@patch(f"{class_path}._format_covariance_value", side_effect=lambda v: round(v))
@patch(f"{class_path}._covariance_dir", return_value=fixtures_folder)
def test_generate_covariance_country(*args):
    weights = {'first': {'weight': 0.6}, 'second': {'weight': 0.4}}
    data = generate_covariance_country(weights)
    assert data['covarianceMatrixIds'] == [
        'inputs.pesticideUnspecifiedAi',
        'inputs.ureaKgN',
        'products.oilPalmFruit'
    ]
    assert data['covarianceMatrix'] == [
        [650, 0.0, 0.0],
        [2364, 9455, 0.0],
        [3632, 14364, 21850.0]
    ]
