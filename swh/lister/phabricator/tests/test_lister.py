# Copyright (C) 2019 the Software Heritage developers
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import re
import json
import unittest

import requests_mock

from swh.lister.core.tests.test_lister import HttpListerTester
from swh.lister.phabricator.lister import PhabricatorLister
from swh.lister.phabricator.lister import get_repo_url


class PhabricatorListerTester(HttpListerTester, unittest.TestCase):
    Lister = PhabricatorLister
    # first request will have the after parameter empty
    test_re = re.compile(r'\&after=([^?&]*)')
    lister_subdir = 'phabricator'
    good_api_response_file = 'api_response.json'
    good_api_response_undefined_protocol = 'api_response_undefined_'\
                                           'protocol.json'
    bad_api_response_file = 'api_empty_response.json'
    # first_index must be retrieved through a bootstrap process for Phabricator
    first_index = None
    last_index = 12
    entries_per_page = 10

    convert_type = int

    def request_index(self, request):
        """(Override) This is needed to emulate the listing bootstrap
        when no min_bound is provided to run
        """
        m = self.test_re.search(request.path_url)
        idx = m.group(1)
        if idx == str(self.last_index):
            return int(idx)

    def get_fl(self, override_config=None):
        """(Override) Retrieve an instance of fake lister (fl).

        """
        if override_config or self.fl is None:
            credentials = {'phabricator': {'fake': [
                {'password': 'toto'}
            ]}}
            override_config = dict(credentials=credentials,
                                   **(override_config or {}))
            self.fl = self.Lister(url='https://fakeurl', instance='fake',
                                  override_config=override_config)
            self.fl.INITIAL_BACKOFF = 1

        self.fl.reset_backoff()
        return self.fl

    def test_get_repo_url(self):
        f = open('swh/lister/%s/tests/%s' % (self.lister_subdir,
                                             self.good_api_response_file))
        api_response = json.load(f)
        repos = api_response['result']['data']
        for repo in repos:
            self.assertEqual(
                'https://forge.softwareheritage.org/source/%s.git' %
                (repo['fields']['shortName']),
                get_repo_url(repo['attachments']['uris']['uris']))

        f = open('swh/lister/%s/tests/%s' %
                 (self.lister_subdir,
                  self.good_api_response_undefined_protocol))
        repo = json.load(f)
        self.assertEqual(
                'https://svn.blender.org/svnroot/bf-blender/',
                get_repo_url(repo['attachments']['uris']['uris']))

    @requests_mock.Mocker()
    def test_full_listing(self, http_mocker):
        fl = self.create_fl_with_db(http_mocker)

        fl.run()

        self.assertEqual(fl.db_last_index(), self.last_index)
        ingested_repos = list(fl.db_query_range(self.first_index,
                                                self.last_index))
        self.assertEqual(len(ingested_repos), self.entries_per_page)
