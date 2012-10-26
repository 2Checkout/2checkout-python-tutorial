import web
import datetime
import twocheckout
from web.contrib.auth import DBAuth
web.config.debug = False

urls = (
    '/', 'index',
    '/login', 'login',
    '/logout', 'logout',
    '/content', 'content',
    '/register', 'register',
    '/success', 'success',
    '/order', 'order',
    '/notification', 'notification',
    '/cancel', 'cancel',
    '/update', 'update',
)

app = web.application(urls, locals())
db = web.database(dbn='mysql', db='pyweb', user='root', passwd='password')
render = web.template.render('templates/')
settings = {}
auth = DBAuth(app, db, **settings)

class index:
    def GET(self):
        return render.index()
    def POST(self):
        return render.index()

class login:
    def GET(self):
        return render.login()
    def POST(self):
        params = web.input()
        user = auth.authenticate(login=params['username'], password=params['password'])
        if user:
            auth.login(user)
            raise web.seeother('/content')
        else:
            raise web.seeother('/')

class logout:
    def GET(self):
        auth.logout()
        raise web.seeother('/')

    def POST(self):
        auth.logout()
        raise web.seeother('/')


class register:
    def GET(self):
        return render.register()

    def POST(self):
        params = web.input()
        if auth.userExist(params['username']):
            return render.register()
        else:
            data = dict()
            data['user_email'] = params['email']
            auth.createUser(params['username'], params['password'], perms=[], **data)
            user = auth.authenticate(login=params['username'], password=params['password'])
            auth.login(user)
            raise web.seeother('/order')

class order:
    def GET(self):
        user = auth.getUser()

        # Pass sale to 2Checkout
        params = {
            'sid': '1817037',
            'mode': '2CO',
            'li_1_type': 'product',
            'li_1_name': 'Subscription',
            'li_1_price': '1.00',
            'li_1_recurrence': '1 Month',
            'merchant_order_id': user.user_login
        }
        link = twocheckout.Charge.link(params)
        raise web.seeother(link)

class content:
    @auth.protected(perm='user')
    def GET(self):
        return render.content()

    @auth.protected(perm='user')
    def POST(self):
        params = web.input()
        if 'logout' in params:
            raise web.seeother('/logout')
        else:
            raise web.seeother('/content')

class success:
    def GET(self):
        params = web.input()
        params['secret'] = 'tango'
        result = twocheckout.Passback.check(params)

        if result.response_code == 'SUCCESS':

            # Update the user and give them credentials
            user_login = params['merchant_order_id']
            user = auth.getUser(user_login)
            data = dict()
            data['last_billed'] = datetime.datetime.now()
            data['last_invoice'] = params['invoice_id']
            data['order_number'] = params['order_number']
            data['2co_status'] = 'active'
            data['date_expire'] = datetime.datetime.now() + datetime.timedelta(1*365/12)
            auth.updateUser(user_login, **data)
            auth.addPermission('user', user.user_id)

            # Return buyer to success page
            return render.success()
        else:

            # Return buyer to fail page
            return render.fail()

    def POST(self):
        params = web.input()
        params['secret'] = 'tango'
        result = twocheckout.Passback.check(params)

        if result.response_code == 'SUCCESS':

            # Update the user and give them credentials
            user_login = params['merchant_order_id']
            user = auth.getUser(user_login)
            data = dict()
            data['last_billed'] = datetime.datetime.now()
            data['last_invoice'] = params['invoice_id']
            data['order_number'] = params['order_number']
            data['2co_status'] = 'active'
            data['date_expire'] = datetime.datetime.now() + datetime.timedelta(1*365/12)
            auth.updateUser(user_login, **data)
            auth.addPermission('user', user.user_id)

            # Return buyer to success page
            return render.success()
        else:

            # Return buyer to fail page
            return render.fail()

class notification:
    def POST(self):

        # Check validity of response
        params = web.input()
        params['secret'] = 'tango'
        result = twocheckout.Notification.check(params)

        if result.response_code == 'SUCCESS':

            # Handle Fraud Failure Message
            if params['message_type'] == 'FRAUD_STATUS_CHANGED' and params['fraud_status'] == 'fail':
                user_login = params['vendor_order_id']
                user = auth.getUser(user_login)
                data = dict()
                data['2co_status'] = 'failed'
                auth.updateUser(user_login, **data)
                auth.removePermission('user', user.user_id)

            # Handle Recurring Success Message
            elif params['message_type'] == 'RECURRING_INSTALLMENT_SUCCESS':
                user_login = params['vendor_order_id']
                user = auth.getUser(user_login)
                data = dict()
                data['last_billed'] = datetime.datetime.now()
                data['last_invoice'] = params['invoice_id']
                data['2co_status'] = 'active'
                data['date_expire'] = user.last_billed + datetime.timedelta(1*365/12)
                auth.updateUser(user_login, **data)
                auth.addPermission('user', user.user_id)

            # Handle Recurring Failed Message
            elif params['message_type'] == 'RECURRING_INSTALLMENT_FAILED':
                user_login = params['vendor_order_id']
                data = dict()
                data['last_billed'] = datetime.datetime.now()
                data['last_invoice'] = params['invoice_id']
                data['2co_status'] = 'declined'
                auth.updateUser(user_login, **data)
                user = auth.getUser(user_login)
                auth.removePermission('user', user.user_id)
            return 'Message Success: ' + params['message_type']
        else:

            # Hash does not match, print fail message for debugging
            return 'Message Fail: ' + params['message_type']

class cancel:
    @auth.protected(perm='user')
    def GET(self):
        return render.cancel()

    @auth.protected(perm='user')
    def POST(self):
        user = auth.getUser()
        data = dict()
        data['2co_status'] = 'canceled'
        auth.updateUser(user.user_login, **data)
        auth.removePermission('user', user.user_id)

        # Set 2Checkout API credentials
        twocheckout.Api.credentials({'username':'APIuser1817037', 'password':'APIpass1817037'})

        # Stop recurring sale
        params = {
        'sale_id': user.order_number
        }
        sale = twocheckout.Sale.find(params)
        sale.stop()

        # Calculate refund amount
        remaining_days = user.date_expire - datetime.datetime.now()
        refund_amount = round((1.00 / 30) * remaining_days.days, 2)

        # Issue refund for remaining amount
        params = {
            'comment': "Refunding Remaining Balance",
            'category': 5,
            'amount': refund_amount,
            'currency': "vendor"
            }
        invoice = max(sale.invoices)
        invoice.refund(params)

        raise web.seeother('/')


if __name__ == "__main__":
    app.run()
