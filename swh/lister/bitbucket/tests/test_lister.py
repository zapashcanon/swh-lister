# Copyright (C) 2017-2019 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import re
import unittest

from datetime import timedelta

from urllib.parse import unquote

import iso8601
import requests_mock

from swh.lister.bitbucket.lister import BitBucketLister
from swh.lister.core.tests.test_lister import HttpListerTester


def convert_type(req_index):
    """Convert the req_index to its right type according to the model's
       "indexable" column.

    """
    return iso8601.parse_date(unquote(req_index))


class BitBucketListerTester(HttpListerTester, unittest.TestCase):
    Lister = BitBucketLister
    test_re = re.compile(r'/repositories\?after=([^?&]+)')
    lister_subdir = 'bitbucket'
    good_api_response_file = 'data/https_api.bitbucket.org/response.json'
    bad_api_response_file = 'data/https_api.bitbucket.org/empty_response.json'
    first_index = convert_type('2008-07-12T07:44:01.476818+00:00')
    last_index = convert_type('2008-07-19T06:16:43.044743+00:00')
    entries_per_page = 10
    convert_type = staticmethod(convert_type)

    def request_index(self, request):
        """(Override) This is needed to emulate the listing bootstrap
        when no min_bound is provided to run
        """
        m = self.test_re.search(request.path_url)
        idx = convert_type(m.group(1))
        if idx == self.Lister.default_min_bound:
            idx = self.first_index
        return idx

    @requests_mock.Mocker()
    def test_fetch_none_nodb(self, http_mocker):
        """Overridden because index is not an integer nor a string

        """
        http_mocker.get(self.test_re, text=self.mock_response)
        fl = self.get_fl()

        self.disable_scheduler(fl)
        self.disable_db(fl)

        # stores no results
        fl.run(min_bound=self.first_index - timedelta(days=3),
               max_bound=self.first_index)

    def test_is_within_bounds(self):
        fl = self.get_fl()
        self.assertTrue(fl.is_within_bounds(
            iso8601.parse_date('2008-07-15'),
            self.first_index, self.last_index))
        self.assertFalse(fl.is_within_bounds(
            iso8601.parse_date('2008-07-20'),
            self.first_index, self.last_index))
        self.assertFalse(fl.is_within_bounds(
            iso8601.parse_date('2008-07-11'),
            self.first_index, self.last_index))


def test_lister_bitbucket(swh_listers, requests_mock_datadir):
    """Simple bitbucket listing should create scheduled tasks

    """
    lister = swh_listers['bitbucket']

    lister.run()

    r = lister.scheduler.search_tasks(task_type='load-hg')
    assert len(r) == 10

    for row in r:
        assert row['type'] == 'load-hg'
        # arguments check
        args = row['arguments']['args']
        assert len(args) == 1

        url = args[0]
        assert url.startswith('https://bitbucket.org')

        # kwargs
        kwargs = row['arguments']['kwargs']
        assert kwargs == {}

        assert row['policy'] == 'recurring'
        assert row['priority'] is None
