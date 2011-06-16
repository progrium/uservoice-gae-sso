import base64
import urllib
from datetime import datetime
from datetime import timedelta

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required

import multipass

def routes():
    return [('/sso/(.+)', SSOHandler),
            ('/admin', AdminHandler),
            ('/', Redirect('/admin')),]

def Redirect(path):
    """ Convenience RequestHandler that simply redirects to a path """
    class RedirectHandler(webapp.RequestHandler):
        def get(self):
            self.redirect(path)
    return RedirectHandler
    
class Config(db.Model):
    account = db.StringProperty(default='')
    api_key = db.StringProperty(default='')
    domain = db.StringProperty(default='')

    @classmethod
    def get(cls):
        return cls.all().get()

class SSOHandler(webapp.RequestHandler):
    def get(self, action):
        config = Config.get()
        action = urllib.unquote(action)
        to = "http://%s%s" % (config.domain, self.request.GET.get('return', '/'))
        if action.startswith('login'):
            user = users.get_current_user()
            if user:
                if ':' in action:
                    action, to = action.split(":")
                    to = base64.b64decode(to)
                token = multipass.token(
                    dict(guid=user.email(), 
                        email=user.email(), 
                        display_name=user.email().split('@')[0], 
                        expires=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')),
                    api_key=config.api_key,
                    account_key=config.account)
                self.redirect("%s?sso=%s" % (to, urllib.quote(token)))
            else:
                to = base64.b64encode(to)
                self.redirect(users.create_login_url('/sso/login:%s' % to))
        elif action.startswith('logout'):
            user = users.get_current_user()
            if user:
                to = base64.b64encode(to or self.request.referrer)
                self.redirect(users.create_logout_url('/sso/logout:%s' % to))
            else:
                try:
                    action, to = action.split(":")
                    to = base64.b64decode(to)
                except ValueError:
                    pass
                self.redirect(to)

class AdminHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url())
        else:
            logout_url = users.create_logout_url('/')
            config = Config.get()
            if not config:
                config = Config()
            self.response.out.write(template.render('admin.html', locals()))
    
    def post(self):
        user = users.get_current_user()
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url())
        else:
            config = Config.get()
            if not config:
                config = Config()
            config.account = self.request.get('account')
            config.api_key = self.request.get('api_key')
            config.domain = self.request.get('domain')
            config.put()
            self.redirect('/admin')

def main():
    application = webapp.WSGIApplication(routes(), debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
