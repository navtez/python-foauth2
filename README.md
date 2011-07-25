# Overview

This is a fork of a fork of a fork. See (http://github.com/OfflineLabs/python-oauth2) for that history. A number of notable differences exist between this code and its forefathers:

* 0% unit test coverage.

* Lightweight at less than 200 lines, including blanks and docstrings.

* Completely removed all the OAuth 1.0 code.

* Completely removed all non-stdlib dependencies (goodbye httplib2, you won't be missed!).

* Implements a later version of the spec than it's parent.

* I'm not sure which version but google's auth2 API accepts this implementation.

# goo.gl URL shortener example

    client_id = 'xxxx.apps.googleusercontent.com'
    client_secret = 'xyzzy'
    auth_url = 'https://accounts.google.com/o/oauth2/auth'
    access_url = 'https://accounts.google.com/o/oauth2/token'
    scope = 'https://www.googleapis.com/auth/urlshortener'
    redirect_url = 'http://localhost/'

    import urlprase
    import foauth2
    client = foauth2.Client(client_id, client_secret)
    print "cut-n-paste the following URL to start the auth dance",
    print client.authorization_url(auth_url, redirect_url=redirect_url, scope=scope)
    print "and copy the resulting link below"
    answer = raw_input()

    query_str = urlparse.urlparse(url_str).query
    params = urlparse.parse_qs(query_str, keep_blank_values=True)
    code = params['code'][0]
    access_token, refresh_token = client.access_token(access_url, code=code, scope=scope)

    print "now you can use %r to GET short urls from goo.gl" % access_token
