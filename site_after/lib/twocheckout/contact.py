from api_request import Api


class Contact:

    @classmethod
    def retrieve(cls, params=None):
        if params is None:
            params = dict()
        url = 'acct/detail_contact_info'
        return Api.call(url, params)
