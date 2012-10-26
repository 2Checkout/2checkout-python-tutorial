from api_request import Api


class Company:

    @classmethod
    def retrieve(cls, params=None):
        if params is None:
            params = dict()
        url = 'acct/detail_company_info'
        return Api.call(url, params)
