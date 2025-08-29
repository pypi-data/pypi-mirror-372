from hestia_earth.schema import SchemaType, SiteDefaultMethodClassification
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.model import linked_node

from . import _aggregated_node, sum_data, _aggregated_version, format_aggregated_list
from .term import _format_country_name, get_by_id
from .blank_node import cleanup_blank_nodes
from .source import format_aggregated_sources
from .measurement import new_measurement
from .management import new_management


def _format_aggregate(new_func: dict):
    def format(aggregate: dict):
        return _aggregated_version(new_func(aggregate))
    return format


def format_site_results(data: dict):
    measurements = data.get('measurements', [])
    management = data.get('management', [])
    return ({
        'measurements': cleanup_blank_nodes(map(_format_aggregate(new_measurement), measurements)),
    } if measurements else {}) | ({
        'management': cleanup_blank_nodes(map(_format_aggregate(new_management), management))
    } if management else {})


def format_site(site_data: dict, sites: list):
    sites = sites or [site_data]
    return create_site(sites[0]) | format_site_results(site_data) | {
        'aggregatedSites': format_aggregated_list('Site', sites),
        'aggregatedSources': format_aggregated_sources(sites, 'defaultSource'),
        'numberOfSites': sum_data(sites, 'numberOfSites')
    }


def _site_id(n: dict, include_siteType: bool):
    return '-'.join(non_empty_list([
        _format_country_name(n),
        n.get('siteType') if include_siteType else None
    ]))


def _site_name(n: dict, include_siteType: bool):
    return ' - '.join(non_empty_list([
        _format_country_name(n, as_id=False),
        n.get('siteType') if include_siteType else None
    ]))


def _site_country_region(data: dict):
    # if region is level > 0, then need to add region and country
    return (
        {'region': linked_node(data)} if data.get('gadmLevel', 0) > 0 else {}
    ) | (
        {'country': linked_node(data if data.get('gadmLevel', 0) == 0 else get_by_id(data.get('@id', '')[0:8]))}
    )


def create_site(data: dict, include_siteType=True):
    site = {'type': SchemaType.SITE.value}
    site['siteType'] = data['siteType']
    site['name'] = _site_name(data, include_siteType)
    site['id'] = _site_id(data, include_siteType)
    site['defaultMethodClassification'] = SiteDefaultMethodClassification.MODELLED.value
    site['defaultMethodClassificationDescription'] = 'aggregated data'
    site['dataPrivate'] = False
    site['aggregatedDataValidated'] = False
    return _aggregated_node(site) | _site_country_region(data['country'])


def update_site(country: dict, source: dict = None, include_siteType=True):
    def update(site: dict):
        site = site | _site_country_region(country)
        site['name'] = _site_name(site, include_siteType)
        site['id'] = _site_id(site, include_siteType)
        return site | ({} if source is None else {'defaultSource': source})
    return update
