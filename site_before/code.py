import web
import json
import datetime
from web.contrib.auth import DBAuth
web.config.debug = False

urls = (
    '/', 'index',
    '/login', 'login',
    '/logout', 'logout',
    '/content', 'content',
    '/register', 'register',
    '/success', 'success',
)

app = web.application(urls, locals())
db = web.database(dbn='mysql', db='site', user='root', passwd='')
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
            auth.addPermission('user', user.user_id)
            raise web.seeother('/success')

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
        return render.success()

    def POST(self):
        return render.success()


if __name__ == "__main__":
    app.run()
