"""
OAuth2.0a 'Bearer Token' handling.
Based on https://github.com/OfflineLabs/python-oauth2/
  * rips out all the httplib2 stuff
  * rips out all the OAuth1.0a stuff
  * based on the newest version of the spec[1] instead of the initial version

[1] http://tools.ietf.org/html/draft-ietf-oauth-v2-18
    http://tools.ietf.org/html/draft-ietf-oauth-v2-bearer-06

The MIT License

Portions Copyright (c) 2011 Jack Diederich c/o HiveFire Inc.
Portions Copyright (c) 2007 Leah Culver, Joe Stump, Mark Paschal, Vic Fryzel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import urllib
import urllib2
import urlparse

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl

try:
    import simplejson
except ImportError:
    # Have django or are running in the Google App Engine?
    from django.utils import simplejson

VERSION = '0.9'

class Error(RuntimeError):
    """Generic exception class."""

    def __init__(self, message='OAuth error occured.'):
        self._message = message

    @property
    def message(self):
        """A hack to get around the deprecation errors in 2.6."""
        return self._message

    def __str__(self):
        return self._message

class Client(object):
    """ Client for OAuth 2.0 'Bearer Token' """

    def __init__(self, client_id, client_secret, redirect_uri=None,
                 timeout=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.timeout = timeout

        if self.client_id is None or self.client_secret is None:
            raise ValueError("Client_id and client_secret must be set.")

    @staticmethod
    def _split_url_string(param_str):
        """Turn URL string into parameters."""
        parameters = parse_qs(param_str, keep_blank_values=False)
        for key, val in parameters.iteritems():
            parameters[key] = urllib.unquote(val[0])
        return parameters

    def authorization_url(self, uri, redirect_uri=None, scope=None):
        """ Get the URL to redirect the user for client authorization """
        if redirect_uri is None:
            redirect_uri = self.redirect_uri

        params = {'client_id' : self.client_id,
                  'redirect_uri' : redirect_uri,
                  'response_type' : 'code',
                 }
        if scope:
            params['scope'] = scope

        return '%s?%s' % (uri, urllib.urlencode(params))

    def access_token(self, uri, redirect_uri=None, code=None, scope=None):
        """Get an access token from the supplied code """

        # prepare required args
        if code is None:
            raise ValueError("Code must be set.")
        if redirect_uri is None:
            redirect_uri = self.redirect_uri
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type' : 'authorization_code',
        }
        print "DATA", data
        if scope is not None:
            data['scope'] = scope
        body = urllib.urlencode(data)

        headers = {'content-type' : 'application/x-www-form-urlencoded',
                   'user_agent' : 'HiveFire-OAuth2a',
                  }

        print (uri, body, headers)
        response = self.request(uri, body=body, method='POST', headers=headers)
        if not response.code == 200:
            raise Error(response.read())
        response_args = simplejson.loads(response.read())

        error = response_args.pop('error', None)
        if error is not None:
            raise Error(error)

        return response_args['access_token'], response_args['refresh_token']

    def refresh(self, uri, refresh_token, secret_type=None):
        """  Get a new access token from the supplied refresh token """

        if refresh_token is None:
            raise ValueError("Refresh_token must be set.")

        # prepare required args
        args = {
            'type': 'refresh',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
        }

        # prepare optional args
        if secret_type is not None:
            args['secret_type'] = secret_type

        body = urllib.urlencode(args)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = self.request(uri, method='POST', body=body, headers=headers)
        if not response.code == 200:
            raise Error(response.read())

        response_args = Client._split_url_string(content)
        return response_args

    def request(self, uri, body=None, headers=None, method='GET'):
        if method == 'POST' and body is None:
            raise ValueError('POST requests must have a body')
        request = urllib2.Request(uri, body, headers)
        return urllib2.urlopen(request, timeout=self.timeout)
