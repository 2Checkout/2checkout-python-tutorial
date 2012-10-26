import hashlib


class Passback:

    @classmethod
    def check_hash(cls, params=None):
        m = hashlib.md5()
        m.update(params['secret'])
        m.update(params['sid'])
        m.update(params['order_number'])
        m.update(params['total'])
        check_hash = m.hexdigest()
        check_hash = check_hash.upper()
        if check_hash == params['key']:
            return True
        else:
            return False

    @classmethod
    def check(cls, params=None):
        if params is None:
            params = dict()
        if 'order_number' in params and 'total' in params:
            check = Passback.check_hash(params)
            if check:
                return '{"code":"SUCCESS","message":"Hash Matched"}'
            else:
                return '{"code":"FAILED","message":"Hash Mismatch"}'
        else:
            return '{"code":"ERROR","message":"You must pass secret word, sid, order_number, total"}'
