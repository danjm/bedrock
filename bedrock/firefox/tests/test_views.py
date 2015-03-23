# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.test.client import RequestFactory
from django.test.utils import override_settings

from mock import patch
from funfactory.urlresolvers import reverse
from nose.tools import ok_

from bedrock.firefox.views import firefox_os_geo_redirect
from bedrock.mozorg.tests import TestCase


FXOS_COUNTRIES = {
    'default': '2.0',
    'AU': '1.3',
    'IN': '1.3T',
    'BR': '1.1',
    'BD': '1.4',
}


class TestFirefoxNew(TestCase):
    def test_frames_allow(self):
        """
        Bedrock pages get the 'x-frame-options: DENY' header by default.
        The firefox/new page needs to be framable for things like stumbleupon.
        Bug 1004598.
        """
        with self.activate('en-US'):
            resp = self.client.get(reverse('firefox.new'))

        ok_('x-frame-options' not in resp)


@override_settings(FIREFOX_OS_COUNTRY_VERSIONS=FXOS_COUNTRIES)
class TestFirefoxOSGeoRedirect(TestCase):
    def setUp(self):
        patcher = patch('bedrock.firefox.views.get_country_from_request')
        self.geo_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def _request(self, country):
        self.geo_mock.return_value = country
        request = RequestFactory().get('/firefox/os/')
        return firefox_os_geo_redirect(request)

    def test_default_version(self):
        """Should redirect to default version if country not in list."""
        resp = self._request('US')
        self.assertTrue(resp['Location'].endswith('/firefox/os/2.0/'))

        resp = self._request('XX')
        self.assertTrue(resp['Location'].endswith('/firefox/os/2.0/'))

    def test_country_specific_versions(self):
        """Should redirect to country appropriate version."""
        resp = self._request('AU')
        self.assertTrue(resp['Location'].endswith('/firefox/os/1.3/'))

        resp = self._request('IN')
        self.assertTrue(resp['Location'].endswith('/firefox/os/1.3t/'))

        resp = self._request('BR')
        self.assertTrue(resp['Location'].endswith('/firefox/os/1.1/'))

        resp = self._request('BD')
        self.assertTrue(resp['Location'].endswith('/firefox/os/1.4/'))
