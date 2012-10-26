Tutorial
=====================

In this tutorial we will walk through integrating the 2Checkout payment method into an existing user management application built on Web.py 0.37 and TwitterBootstrap 2.1.0. This demo application also utilizes the webpy_auth user authentication library. The source for the example application used in this tutorial can be accessed in this Github repository.

Setting up the Example Application
----------------------------------

We need an existing example application to demonstrate the integration so lets download or clone the 2checkout-python-tutorial tutorial application.

```shell
$ git clone https://github.com/2checkout/2checkout-python-tutorial.git
```

This repository contains both an example before and after application so that we can follow along with the tutorial using the site\_before app and compare the result with the site\_after app. We can start by moving the site\_before directory to the webroot directory on our server and lets rename it to web-widgets which is the name of our example site.

Now we need to create our database.

```shell
create database webwidgets;
```

Next we run the schema.sql file on our database.

```shell
mysql webwidgets < schema.sql -u <mysql username> -p
```

Now we can specify our database credentials in our application.

code.py
```python
db = web.database(dbn='mysql', db='site', user='root', passwd='')
```

Let's go ahead and startup the example application.

```shell
cd web-widgets
python code.py
```

We can then view it at [http://localhost:8080](http://localhost:8080).

![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-1.png)

You can see that this site requires users to signup for a membership to access the web-widget content pages.

Adding the routes
-----------------

In this tutorial, we will integrate the 2Checkout payment method so that the user must order a recurring monthly membership before gaining access to the content. We will also setup a listener that will be responsible for updating user access for the contact based on the Notifications that 2Checkout sends on their recurring billing status. Finially we will utilize 2Checkout's API to provide user with the ability to update their billing information and cancel their recurring membership. We already have a route that we can use for the success callback, so let go ahead an setup the URL's for the other classes we will create.

code.py
```python
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
```

Setting up the 2Checkout Python Library
------------------------------------
2Checkout's Python library provides us with a simple bindings to the API, INS and Checkout process so that we can integrate each feature with only a few lines of code. We can download or clone the library at [https://github.com/2checkout/2checkout-python](https://github.com/2checkout/2checkout-python).

Including the library is as easy as copying the **twocheckout** directory to our application's **lib** directory and then we can import the library.

code.py
```python
import twocheckout
```

Now we can integrate with any 2Checkout feature using only a couple lines of code.

Setup Order
-----------
Let's take a look at our current registration process.

code.py
```python
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
            auth.addPermission('user', user.user_id)
            raise web.seeother('/success')
```

As you can see, we are currently loading the registration form where we can handle the field validation and pass the data back into the register class by POST. We now want to pass the user to 2Checkout to pay for the membership before we activate them. To accomplish this, lets first remove the `auth.addPermission('user', user.user_id)` from our register class. We will add permissions later in the success class. We will also need to swap the "/success" redirect for an "/order" redirect and create our new order class.

```python
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
```

Lets take a look at what we did here. First we grabbed the user object for this user.

```python
user = auth.getUser()
```

Then we create an array of sale parameters to pass to 2Checkout using the Pass-Through-Products parameter set and we assign the `user_login` to the `merchant_order_id` parameter. _(The value passed with the `merchant_order_id parameter` will be passed back to our approved URL and will be returned using the `vendor_order_id` parameter on all INS messages pertaining to the sale.)_

```python
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
```

Then we pass the parameters and the buyer to our custom checkout page on 2Checkout's secure server to complete the order.

```python
raise web.seeother(link)
```

Passback
--------

When the order is completed, 2Checkout will return the buyer and the sale parameters to the URL that we specify as the approved URL in our account. This URL can also be passed in dynamically for each sale using the `x_receipt_link_url` parameter.

We will pass the buyer back to the success url, so we will need to make some changes to our success class to handle the passback.

code.py
```python
class success:
    def GET(self):
        params = web.input()
        params['secret'] = 'tango'
        result = twocheckout.Passback.check(params)
        result = json.loads(result)

        if result['response']['code'] == 'SUCCESS':

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

        if result['response']['code'] == 'SUCCESS':

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
```

First we grab all of the parameters returned by 2Checkout and assign them to the `params` dictionary. We also add our secret word to the params dictionary with `secret` as the key.

```python
params = web.input()
params['secret'] = 'tango'
```

Then we pass the array and our secret word to the `twocheckout.Passback.check()` binding and check the result.

```python
result = twocheckout.Passback.check(params)
```

If the result if successful `result.response_code == 'SUCCESS'`, we give the user access to the content and display the order success page. If the response is not successful `result.response_code == 'FAIL'`, we display the order failed page.

```python
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
```

Now we can setup our return method, enter our secret word and provide the approved URL path "http://localhost:8080/success" under the Site Management page in our 2Checkout admin.

**Site Management Page**
![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-2.png)

**Lets try it out with a live sale.**
![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-3.png)

**Enter in our billing information and submit the payment.**
![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-4.png)

**Success Page.**
![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-5.png)

Now the user is activated and can login to access the content that they paid for.
![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-6.png)

Notifications
-------------

2Checkout will send notifications to our application under the following circumstances.

* Order Created
* Fraud Status Changed
* Shipping Status Changed
* Invoice Status Changed
* Refund Issued
* Recurring Installment Success
* Recurring Installment Failed
* Recurring Stopped
* Recurring Complete
* Recurring Restarted

For our application, we are interested in the Fraud Status Changed message to disable the user if the sale fails fraud review, Recurring Installment Failed message to disable the user if their sale fails to bill successfully, and the Recurring Installment Success message to re-enable a disabled user.

Based on these requirements, lets go ahead and setup our notification class.

code.py
```python
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

```

We grab the message parameters and assign each key/value pair to our params dictionary. We also add our secret word to the dictionary using the `secret` key just like we did in the success class.

```python
params = web.input()
params['secret'] = 'tango'
```

Then we pass the params dict to the `twocheckout.Notification.check()` binding, load the JSON response to a dictionary, and check the result.

```python
result = twocheckout.Notification.check(params)
result = json.loads(result)
```

If the response is successful `result.response_code == 'SUCCESS'`, we can preform actions based on the `message_type` parameter value.

For the Fraud Status Changed message, we will also check the value of the `fraud_status` parameter and disable the user if it equals 'fail'.

```python
if params['message_type'] == 'FRAUD_STATUS_CHANGED' and params['fraud_status'] == 'fail':
    user_login = params['vendor_order_id']
    user = auth.getUser(user_login)
    data = dict()
    data['2co_status'] = 'failed'
    auth.updateUser(user_login, **data)
    auth.removePermission('user', user.user_id)
```

For the Recurring Installment Failed message we will disable the user.

```python
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
```

For the Recurring Installment Success message we will enable the user.

```python
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
```

Now we can setup our Notification URL path "http://localhost:8080/notification" and enable each message under the Notifications page in our 2Checkout admin.

![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-7.png)

Lets test our notification function. Now there are a couple ways to go about this. You can wait for the notifications to come on a live sale, or just head over to the [INS testing tool](http://developers.2checkout.com/inss) and test the messages right now. Remember the MD5 hash must match so for easy testing, you must compute the hash based on like below:

`UPPERCASE(MD5_ENCRYPTED(sale\_id + vendor\_id + invoice\_id + Secret Word))`

You can just use an [online MD5 Hash generator](https://www.google.com/webhp?q=md5+generator) and convert it to uppercase.

Cancel
------

We want to provide the user with the ability to cancel their membership and recurring billing without having to contact us. To cancel the recurring billing we will use the Sale stop binding to cancel all active recurring lineitems on the sale.

To accomplish this we will setup a cancel confirmation template and a cancel class.

templates/cancel.html
```html
<div class="container">
    <h1>Are you sure?</h1>
    <p>Click the confirm button to cancel the recurring billing on your membership.</p>
    <p>We will refund you for your unused time with in 3-7 days.</p>
    <form class="form-horizontal" id="login-form" action="/cancel" method="post">
        <input type="hidden" name="confirm" id="confirm">
        <div class="control-group">
            <div class="controls">
                <button type="submit" class="btn btn-primary btn-large">Cancel Membership</button>
            </div>
        </div>
    </form>
</div>
```


code.py
```python
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
```

Our cancel class loads our cancel template for our user to confirm.

![](http://github.com/2checkout/2checkout-python-tutorial/raw/master/img/webwidgets-8.png)

When we get the cancel confirmation from the user, we can use 2Checkout's back office API to cancel the recurring billing.

We set our 2Checkout API username and password using the `twocheckout.Api.credentials()` method.

```python
twocheckout.Api.credentials({'username':'APIuser1817037', 'password':'APIpass1817037'})
```

Now we use the order\_number to retrieve the sale and call the `stop()` method on the sale instance.

```python
params = {
'sale_id': user.order_number
}
sale = twocheckout.Sale.find(params)
result = sale.stop()
```

Since we are going to disable the user, we should also go ahead and refund them for the unused days in their subscription. So we use the last\_billed timestamp for the user to caclulate the unused days in their subscription.

```python
remaining_days = user.date_expire - datetime.datetime.now()
```

We can then apply that to the subscription cost to get the refund amount.

```python
refund_amount = round((1.00 / 30) * remaining_days.days, 2)
```

To submit the refund, we create a new Invoice obejct from the most recent invoice in the Sale object and call the refund() method on it.

```python
params = {
'comment': "Refunding Remaining Balance",
'category': 5,
'amount': refund_amount,
'currency': "vendor"
}
invoice = max(sale.invoices)
invoice.refund(params)
```

Update
------

This last one is easy. 2Checkout provides a page for users to update their billing information on a recurring sale. We could just define the URL in our navbar. But to make it easy for them, lets pass in the order\_number when we redirect them.

`code.py`
```python
class update:
    @auth.protected(perm='user')
    def GET(self):
        user = auth.getUser()

        # Build update billing link
        link = "https://www.2checkout.com/va/sales/customer/change_billing_method?sale_id=" + str(user.order_number)
        raise web.seeother(link)
```

Conclusion
----------

Now our application is fully integrated! Our users can register, pay for their membership and immediatly get access. We update the user based on the 2Checkout INS messages, and we provided the user with the ability to cancel the order or update their billing information.
