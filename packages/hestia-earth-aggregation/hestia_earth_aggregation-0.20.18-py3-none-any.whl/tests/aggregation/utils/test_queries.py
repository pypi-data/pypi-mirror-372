from unittest.mock import Mock, patch

from tests.utils import start_year, end_year
from hestia_earth.aggregation.utils.queries import (
    download_node, download_nodes, find_country_nodes, _global_nodes, find_global_nodes,
    _get_time_ranges, _earliest_date, _latest_date, get_time_ranges, _sub_country_nodes
)

class_path = 'hestia_earth.aggregation.utils.queries'
country_name = 'Japan'
expected_body = '{"test": 1}'


class FakePostRequest():
    def __init__(self, results=[]) -> None:
        self.results = results
        pass

    def json(self):
        return {'results': self.results}


class FakeS3Client():
    def __init__(self, result: dict = {}):
        self.result = result
        pass

    def get_object(self, **kwargs):
        return self.result


class FakeBody():
    def read(self):
        return expected_body


@patch(f"{class_path}._get_s3_client")
@patch(f"{class_path}.download_hestia", return_value={})
def test_download_node(mock_download_hestia: Mock, mock_get_s3_client: Mock):
    node_id = 'id'

    # aggregated Site => download original state
    node_type = 'Site'
    download_node({'aggregated': True, '@type': node_type, '@id': 'id'})
    mock_download_hestia.assert_called_once_with(node_id, node_type, data_state='original')
    mock_download_hestia.reset_mock()

    # aggregate IA => download recalculated
    node_type = 'ImpactAssessment'
    mock_get_s3_client.return_value = FakeS3Client({'Metadata': {'stage': 1, 'maxstage': 1}, 'Body': FakeBody()})
    result = download_node({'aggregated': True, '@type': node_type, '@id': 'id'})
    mock_download_hestia.assert_not_called()
    mock_download_hestia.reset_mock()
    assert result.get('test') == 1

    # non-aggregated Cycle stage 1 of 2 => fail to download recalculated
    node_type = 'ImpactAssessment'
    mock_get_s3_client.return_value = FakeS3Client({'Metadata': {'stage': 1, 'maxstage': 2}, 'Body': FakeBody()})
    result = download_node({'@type': node_type, '@id': 'id'})
    mock_download_hestia.assert_not_called()
    mock_download_hestia.reset_mock()
    assert result is None


@patch(f"{class_path}.download_node", return_value={})
def test_download_nodes(mock_download: Mock):
    nodes = [{}, {}]
    download_nodes(nodes)
    assert mock_download.call_count == len(nodes)


@patch('requests.post', return_value=FakePostRequest())
def test_find_country_nodes(mock_post: Mock):
    find_country_nodes({}, start_year, end_year, {'@id': 'Japan'})
    mock_post.assert_called_once()


@patch('requests.post', return_value=FakePostRequest())
@patch(f"{class_path}.download_nodes", return_value=[])
def test_sub_country_nodes(mock_download: Mock, mock_post: Mock):
    _sub_country_nodes({}, start_year, end_year, {'name': 'Western Europe'})
    mock_download.assert_called_once_with([])
    mock_post.assert_called()


@patch('requests.post', return_value=FakePostRequest())
@patch(f"{class_path}._fetch_countries", return_value=[])
@patch(f"{class_path}.download_nodes", return_value=[])
def test_global_nodes(mock_download: Mock, *args):
    _global_nodes({'name': ''}, start_year, end_year)
    mock_download.assert_called_once_with([])


@patch(f"{class_path}._global_nodes", return_value=[])
@patch(f"{class_path}._sub_country_nodes", return_value=[])
def test_find_global_nodes(mock_find_sub_countries: Mock, mock_find_global: Mock):
    find_global_nodes({}, 0, 0, {'@id': 'region-europe'})
    mock_find_sub_countries.assert_called_once()

    find_global_nodes({}, 0, 0, {'name': 'World'})
    mock_find_global.assert_called_once()


def test__get_time_ranges():
    assert _get_time_ranges('1996', '2021') == [(1990, 2009), (2010, 2025)]
    assert _get_time_ranges('2000', '2020') == [(1990, 2009), (2010, 2025)]
    assert _get_time_ranges('1901', '2001') == [
        (1890, 1909), (1910, 1929), (1930, 1949), (1950, 1969), (1970, 1989), (1990, 2009)
    ]


@patch(f"{class_path}._get_time_ranges", return_value=[(2000, 2009), (2010, 2019)])
@patch(f"{class_path}._latest_date", return_value='2021-01-01')
@patch(f"{class_path}._earliest_date")
def test_get_time_ranges(mock_earliest_date: Mock, *args):
    term = {'name': ''}

    # no earliest date => no time ranges
    mock_earliest_date.return_value = None
    assert len(get_time_ranges(term, term)) == 0

    # with earliest date => time ranges
    mock_earliest_date.return_value = 2000
    assert len(get_time_ranges(term, term)) > 0


@patch(f"{class_path}.search")
def test_earliest_date(mock_search: Mock):
    # no results => no date
    mock_search.return_value = []
    assert not _earliest_date({'name': ''}, {'name': 'World'})

    # with results => first date
    mock_search.return_value = [{'endDate': 2000}, {'endDate': 2010}]
    assert _earliest_date({'name': ''}, {'name': 'Japan'}) == 2000


@patch(f"{class_path}.search")
def test_latest_date(mock_search: Mock):
    # no results => no date
    mock_search.return_value = []
    assert not _latest_date({'name': ''}, {'name': 'World'})

    # with results => first date
    mock_search.return_value = [{'endDate': 2000}, {'endDate': 2010}]
    assert _latest_date({'name': ''}, {'name': 'Japan'}) == 2000
