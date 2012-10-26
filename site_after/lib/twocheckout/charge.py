import urllib


class Charge:

    @classmethod
    def form(cls, params=None):
        if params is None:
            params = dict()
        form = "<form id=\"2checkout\" action=\"https://www.2checkout.com/checkout/spurchase\" method=\"post\">\n"
        for param in params:
            form = form + "<input type=\"hidden\" name=\"" + param + "\" value=\"" + str(params[param]) + "\" />\n"
        form = form + "<input type=\"submit\" value=\"Proceed to Checkout\" />\n</form>\n"
        return form

    @classmethod
    def submit(cls, params=None):
        if params is None:
            params = dict()
        form = "<form id=\"2checkout\" action=\"https://www.2checkout.com/checkout/spurchase\" method=\"post\">\n"
        for param in params:
            form = form + "<input type=\"hidden\" name=\"" + param + "\" value=\"" + str(params[param]) + "\" />\n"
        form = form + "<input type=\"submit\" value=\"Proceed to Checkout\" />\n</form>\n"
        form = form + "<script type=\"text/javascript\">document.getElementById('2checkout').submit();</script>"
        return form

    @classmethod
    def link(cls, params=None, url="https://www.2checkout.com/checkout/spurchase?"):
        if params is None:
            params = dict()
        param = urllib.urlencode(params)
        url = url.endswith('?') and (url + param)
        return url
