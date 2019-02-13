# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2018
#
# This file is part of GWOSC.
#
# GWOSC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWOSC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWOSC.  If not, see <http://www.gnu.org/licenses/>.

import contextlib
import json

from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError

DEFAULT_URL = "https://www.gw-openscience.org"
MAX_GPS = 99999999999


# -- JSON handling ------------------------------------------------------------

def fetch_json(url):
    """Fetch JSON data from a remote URL

    Parameters
    ----------
    url : `str`
        the remote URL to fetch

    Returns
    ------
    json : `object`
        the data fetched from ``url`` as parsed by :func:`json.loads`

    See also
    --------
    json.loads
        for details of the JSON parsing

    Examples
    --------
    >>> from gwpy.io.losc import fetch_json
    >>> fetch_json('https://losc.ligo.org/archive/1126257414/1126261510/json/')
    """
    with contextlib.closing(urlopen(url)) as response:
        data = response.read()
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        try:
            return json.loads(data)
        except ValueError as exc:
            exc.args = ("Failed to parse LOSC JSON from %r: %s"
                        % (url, str(exc)),)
            raise


# -- API calls ----------------------------------------------------------------

def fetch_dataset_json(gpsstart, gpsend, host=DEFAULT_URL):
    """Returns the JSON metadata for all datasets matching the GPS interval

    Parameters
    ----------
    gpsstart : `int`
        the GPS start of the desired interval

    gpsend : `int`
        the GPS end of the desired interval

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    url = '{}/archive/{:d}/{:d}/json/'.format(host, gpsstart, gpsend)
    return fetch_json(url)


def fetch_event_json(event, host=DEFAULT_URL):
    """Returns the JSON metadata for the given event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    url = '{}/archive/{}/json/'.format(host, event)
    return fetch_json(url)


def fetch_run_json(run, detector, gpsstart=0, gpsend=MAX_GPS,
                   host=DEFAULT_URL):
    """Returns the JSON metadata for the given science run parameters

    Parameters
    ----------
    run : `str`
        the name of the science run, e.g. ``'O1'``

    detector : `str`
        the prefix of the GW detector, e.g. ``'L1'``

    gpsstart : `int`
        the GPS start of the desired interval

    gpsend : `int`
        the GPS end of the desired interval

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    url = '{}/archive/links/{}/{}/{:d}/{:d}/json/'.format(
        host, run, detector, gpsstart, gpsend)
    return fetch_json(url)


def fetch_catalog_json(catalog, host=DEFAULT_URL):
    """"Returns the JSON metadata for the given catalogue

    Parameters
    ----------
    catalog : `str`
        the name of the event catalog, e.g. `GWTC-1-confident`

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    json
        the JSON data retrieved from GWOSC and returnend by
        :func:`json.loads`
    """
    url = "{}/catalog/{}/json/".format(
        host, catalog,
    )
    return fetch_json(url)


def fetch_catalog_event_json(event, version=None, host=DEFAULT_URL):
    """Returns the JSON metadata for the given event in a catalog

    This method queries for all available data-release versions, returning
    the highest available version, unless ``version=<X>`` is specified.

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    version : `int`, `None`, optional
        restrict query to a given data-release version

    Returns
    -------
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    # if user specified, just use it
    if version:
        return fetch_json(_catalog_event_url(event, version, host=host))
    # otherwise query from first version and return highest available
    # its inefficient, but it works..
    thisv = 1
    while True:
        url = _catalog_event_url(event, thisv, host=host)
        try:
            data = fetch_json(url)
        except (URLError, ValueError):  # no data for this version
            if thisv == 1:  # first version, so fail
                raise ValueError(
                    "no catalog datasets found for {!r}".format(event),
                )
            # return data from last successful query
            return data
        thisv += 1


def _catalog_event_url(event, version, host=DEFAULT_URL):
    return "{0}/archive/{1}_R{2}/json/".format(
        host,
        event,
        version,
    )
