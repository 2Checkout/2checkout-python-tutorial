import urllib
import urllib2


class Api:

    username = []
    password = []

    @classmethod
    def credentials(cls, credentials):
        Api.username = credentials['username']
        Api.password = credentials['password']

    @classmethod
    def call(cls, method, params=None):
        username = cls.username
        password = cls.password
        headers = {'Accept': 'application/json'}
        base_url = 'https://www.2checkout.com/api/'
        url = base_url + method
        data = urllib.urlencode(params)
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
            None, 'https://www.2checkout.com', username, password
        )
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        try:
            req = urllib2.Request(url, data, headers)
            result = urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            result = e.read()
        return result
