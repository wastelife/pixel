#########################################################################
## Define your tables below; for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

auth.settings.login_next = URL('shares')
auth.settings.logout_next = URL('index')
auth.settings.profile_next = URL('default', 'profile', args=[auth.user_id])
auth.settings.register_next = URL('user', args='login')
auth.settings.change_password_next = URL('shares')
auth.messages.logged_in = None
auth.messages.logged_out = None
auth.messages.profile_updated = None
auth.messages.password_changed = None

from datetime import datetime

# Relation of users: 1 user - n friends
db.define_table('relation',
                Field('user_id'),
                Field('friend'),
)

# Shares (use db.picture to find picture related to this share, use db.message to find messages related to this share)
db.define_table('shares',
                Field('author'),
                Field('title', 'text', default=''),
                Field('information', default=''),
                Field('picture', 'upload'),
                Field('create_time', default=datetime.utcnow()),
                Field('first_name', default=''),
                Field('last_name', default=''),
                Field('votes', 'integer', default=0)
)
db.shares.votes.writable = False
db.shares.title.requires=IS_EMPTY_OR(IS_LENGTH(10, error_message='The number of characters should be less than 20.'))
db.shares.information.requires=IS_EMPTY_OR(IS_LENGTH(100, error_message='The number of characters should be less than 100.'))

# Shave messages of shares (sort by create_time)
db.define_table('messages',
                Field('author'),
                Field('message_content', default=''),
                Field('create_time', default=datetime.utcnow()),
                Field('share_id'),
                Field('first_name', default=''),
                Field('last_name', default='')
)
db.messages.message_content.requires=IS_LENGTH(200, error_message='The number of characters should be less than 200.')