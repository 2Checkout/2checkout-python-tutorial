from api_request import Api


class Product:

    @classmethod
    def create(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/create_product'
        return Api.call(url, params)

    @classmethod
    def retrieve(cls, params=None):
        if params is None:
            params = dict()
        if 'product_id' in params:
            url = 'products/detail_product'
        else:
            url = 'products/list_products'
        return Api.call(url, params)

    @classmethod
    def update(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/update_product'
        return Api.call(url, params)

    @classmethod
    def delete(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/delete_product'
        return Api.call(url, params)
