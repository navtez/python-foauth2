import mock
import unittest

import foauth2


class TestFoauth2(unittest.TestCase):
    def test_section_4_1_3(self):
        # test the parts we care about from http://tools.ietf.org/html/draft-ietf-oauth-v2-20#section-4.1.3
        client = foauth2.Client('client_id', 'client_secret')
        self.assertRaises(ValueError, client.authorization_url)
        redirect_uri = 'http://example.com/'
        client.authorization_url('http://example.com/oauth', redirect_uri=redirect_uri)

        self.assertRaises(ValueError, client.redeem_code)
        self.assertRaises(ValueError, client.redeem_code, code='code')
        client._request = mock.Mock()
        client._request().read._return_value = '{"access_token": "token", "code": "xyzzy"}'
        client._request().code = 200
        self.assertRaises(ValueError, client.redeem_code, code='code', redirect_uri='mismatch')
        client.redeem_code(code='code', redirect_uri=redirect_uri)

        client._authorization_redirect_uri = None
        client.redeem_code(code='code')


if __name__ == '__main__':
    unittest.main()
