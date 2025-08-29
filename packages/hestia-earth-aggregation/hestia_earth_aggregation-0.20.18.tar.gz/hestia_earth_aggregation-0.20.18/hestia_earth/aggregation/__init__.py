from pkgutil import extend_path
from hestia_earth.utils.tools import current_time_ms

from .log import logger
from .aggregate_cycles import run_aggregate
from .recalculate_cycles import should_recalculate, recalculate

__path__ = extend_path(__path__, __name__)


def aggregate(country: dict, product: dict, start_year: int, end_year: int, source: dict = None):
    """
    Aggregates data from HESTIA.
    Produced data will be aggregated by product, country and year.

    Parameters
    ----------
    country: dict
        The country to group the data.
    product: dict
        The product to group the data.
    start_year: int
        The start year of the data.
    end_year: int
        The end year of the data.
    source: dict
        Optional - the source of the generate data. Will be set to HESTIA if not provided.

    Returns
    -------
    list
        A list of aggregations.
        Example: `[<impact_assesment1>, <impact_assesment2>, <cycle1>, <cycle2>]`
    """
    now = current_time_ms()
    logger.info('Aggregating %s in %s for period %s to %s',
                product.get('name'),
                country.get('name'),
                start_year,
                end_year)
    aggregations = run_aggregate(country, product, start_year, end_year, source)
    logger.info('time=%s, unit=ms', current_time_ms() - now)
    return [
        recalculate(agg, product) for agg in aggregations
    ] if should_recalculate(product) else aggregations
