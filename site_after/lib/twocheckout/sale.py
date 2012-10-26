from api_request import Api
from util import Util
import json


class Sale:

    @classmethod
    def retrieve(cls, params=None):
        if params is None:
            params = dict()
        if 'sale_id' in params or 'invoice_id' in params:
            url = 'sales/detail_sale'
        else:
            url = 'sales/list_sales'
        return Api.call(url, params)

    @classmethod
    def refund(cls, params=None):
        if params is None:
            params = dict()
        if 'lineitem_id' in params:
            url = 'sales/refund_lineitem'
        else:
            url = 'sales/refund_invoice'
        return Api.call(url, params)

    @classmethod
    def stop(cls, params=None):
        if params is None:
            params = dict()
        if 'lineitem_id' in params:
            url = 'sales/stop_lineitem_recurring'
            return Api.call(url, params)
        elif 'sale_id' in params:
            url = 'sales/detail_sale'
            sale = Api.call(url, params)
            sale = json.loads(sale)
            if 'response_code' in sale:
                active_lineitems = Util.active(sale['sale']['invoices'])
                if dict(active_lineitems):
                    url = 'sales/stop_lineitem_recurring'
                    result = dict()
                    i = 0
                    for k, v in active_lineitems.items():
                        lineitem_id = v
                        params = {'lineitem_id': lineitem_id}
                        result[i] = Api.call(url, params)
                        i += 1
                    return json.dumps(result, sort_keys=True, indent=4)
                else:
                    return '{"response":{"code":"SUCCESS","message":"No active recurring lineitems"}}'
            else:
                return sale
        else:
            return '{"errors":{"code":"INVALID PARAMETER","message":"You must pass a sale_id or lineitem_id."}}'

    @classmethod
    def active(cls, params=None):
        if params is None:
            params = dict()
        if 'sale_id' in params:
            url = 'sales/detail_sale'
            sale = Api.call(url, params)
            sale = json.loads(sale)
            if 'response_code' in sale:
                active_lineitems = Util.active(sale['sale']['invoices'])
            else:
                return sale
        else:
            return '{"errors":{"code":"INVALID PARAMETER","message":"You must pass a sale_id."}}'
        if dict(active_lineitems):
            response = active_lineitems
        else:
            response = '{"response":{"code":"SUCCESS","message":"No active reurring lineitems"}}'
        return response

    @classmethod
    def comment(cls, params=None):
        if params is None:
            params = dict()
        url = 'sales/create_comment'
        return Api.call(url, params)

    @classmethod
    def ship(cls, params=None):
        if params is None:
            params = dict()
        url = 'sales/mark_shipped'
        return Api.call(url, params)

    @classmethod
    def reauth(cls, params=None):
        if params is None:
            params = dict()
        url = 'sales/reauth'
        return Api.call(url, params)
