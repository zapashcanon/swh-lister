# Copyright (C) 2017-2019 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import re
import unittest

import requests_mock

from datetime import datetime, timedelta

from swh.lister.core.tests.test_lister import HttpListerTester
from swh.lister.github.lister import GitHubLister


class GitHubListerTester(HttpListerTester, unittest.TestCase):
    Lister = GitHubLister
    test_re = re.compile(r'/repositories\?since=([^?&]+)')
    lister_subdir = 'github'
    good_api_response_file = 'data/https_api.github.com/first_response.json'
    bad_api_response_file = 'data/https_api.github.com/empty_response.json'
    first_index = 0
    last_index = 369
    entries_per_page = 100
    convert_type = int

    def response_headers(self, request):
        headers = {'X-RateLimit-Remaining': '1'}
        if self.request_index(request) == self.first_index:
            headers.update({
                'Link': '<https://api.github.com/repositories?since=%s>;'
                        ' rel="next",'
                        '<https://api.github.com/repositories{?since}>;'
                        ' rel="first"' % self.last_index
            })
        else:
            headers.update({
                'Link': '<https://api.github.com/repositories{?since}>;'
                        ' rel="first"'
            })
        return headers

    def mock_rate_quota(self, n, request, context):
        self.rate_limit += 1
        context.status_code = 403
        context.headers['X-RateLimit-Remaining'] = '0'
        one_second = int((datetime.now() + timedelta(seconds=1.5)).timestamp())
        context.headers['X-RateLimit-Reset'] = str(one_second)
        return '{"error":"dummy"}'

    @requests_mock.Mocker()
    def test_scheduled_tasks(self, http_mocker):
        self.scheduled_tasks_test(
            'data/https_api.github.com/next_response.json', 876, http_mocker)


def test_lister_github(swh_listers, requests_mock_datadir):
    """Simple github listing should create scheduled tasks

    """
    lister = swh_listers['github']

    lister.run()

    r = lister.scheduler.search_tasks(task_type='load-git')
    assert len(r) == 100

    for row in r:
        assert row['type'] == 'load-git'
        # arguments check
        args = row['arguments']['args']
        assert len(args) == 1

        url = args[0]
        assert url.startswith('https://github.com')

        # kwargs
        kwargs = row['arguments']['kwargs']
        assert kwargs == {}

        assert row['policy'] == 'recurring'
        assert row['priority'] is None
