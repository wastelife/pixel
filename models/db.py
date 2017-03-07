# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager
from datetime import datetime

auth = Auth(db)
service = Service()
plugins = PluginManager()

## after auth = Auth(db)
auth.settings.extra_fields['auth_user']= [
  Field('introduction', default=''),
  Field('address', default=''),
  Field('contact_email', default=''),
  Field('telephone', default=''),
  Field('avatar', 'upload'),
  Field('create_time', default=datetime.utcnow()),
]
## before auth.define_tables(username=True)

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)
db.auth_user.create_time.writable=db.auth_user.create_time.readable=False
db.auth_user.introduction.requires=IS_EMPTY_OR(IS_LENGTH(200, error_message='The number of characters should be less than 200.'))
db.auth_user.address.requires=IS_EMPTY_OR(IS_LENGTH(50, error_message='The number of characters should be less than 50.'))
db.auth_user.contact_email.requires=IS_EMPTY_OR(IS_EMAIL(error_message='This is not a valid email.'))
db.auth_user.telephone.requires=IS_EMPTY_OR(IS_MATCH('^\d*$', error_message='This is not a valid phone number.'))
db.auth_user.avatar.requires=IS_EMPTY_OR([IS_IMAGE(extensions=('png', 'jpg', 'jpeg'),
                                                  error_message='must be png, jpg and jpeg file.'),
                                          IS_LENGTH(1048576, error_message='must less than 1MB.')])

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

######################
# Logging
import logging, sys
FORMAT = "%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(request.application)
logger.setLevel(logging.INFO)

# Let's log the request.
logger.info("====> Request: %r %r %r %r" % (request.env.request_method, request.env.path_info, request.args, request.vars))
