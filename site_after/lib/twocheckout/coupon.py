from api_request import Api


class Coupon:

    @classmethod
    def create(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/create_coupon'
        return Api.call(url, params)

    @classmethod
    def retrieve(cls, params=None):
        if params is None:
            params = dict()
        if 'coupon_code' in params:
            url = 'products/detail_coupon'
        else:
            url = 'products/list_coupons'
        return Api.call(url, params)

    @classmethod
    def update(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/update_coupon'
        return Api.call(url, params)

    @classmethod
    def delete(cls, params=None):
        if params is None:
            params = dict()
        url = 'products/delete_coupon'
        return Api.call(url, params)
