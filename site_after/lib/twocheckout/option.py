from api_request import Api


class Option:

    @classmethod
    def create(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/create_option'
        return Api.call(url, params)

    @classmethod
    def retrieve(cls, params=None):
        if params is None:
            params = dict()
        if 'option_id' in params:
            url = 'products/detail_option'
        else:
            url = 'products/list_options'
        return Api.call(url, params)

    @classmethod
    def update(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/update_option'
        return Api.call(url, params)

    @classmethod
    def delete(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/delete_option'
        return Api.call(url, params)
