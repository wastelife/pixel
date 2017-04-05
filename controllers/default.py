# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

import io
import re


# @banana
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict()


@auth.requires_login()
def following():
    user_id = long(auth.user_id)
    return dict(user_id=user_id)


@auth.requires_login()
def load_following():
    number = int(request.vars.number)
    user_id = long(request.vars.user_id)
    relations = db(db.relation.user_id == user_id).select(orderby=~db.relation.id)
    # rows = db(db.shares.author==relations[2].friend).select(orderby=~db.shares.create_time)
    rows = []
    for relation in relations:
        row = db(db.shares.author == relation.friend).select(orderby=~db.shares.create_time)
        print row
        for item in row:
            rows.append(item)
    print rows
    return response.json(dict(shares=rows))


@auth.requires_login()
def shares():
    return dict()

@auth.requires_login()
def popular():
    return dict()


@auth.requires_login()
def load_shares():
    number = int(request.vars.number)
    rows = db(db.shares).select(limitby=(0, number), orderby=~db.shares.create_time)
    shares2 = []
    if (request.vars.search):
        pattern = request.vars.search.lower()
        for ele in rows:
            string = ele.title.lower()
            if re.search(pattern, string, flags=0):
                shares2.append(ele)
        return response.json(dict(shares=shares2))
    else:
        return response.json(dict(shares=rows))


@auth.requires_login()
def load_shares2():
    pattern = request.vars.search.lower()
    number = int(request.vars.number)
    rows = db(db.shares).select(limitby=(0, number), orderby=~db.shares.votes)
    shares2 = []
    for ele in rows:
        string = ele.title.lower()
        if re.search(pattern, string, flags=0):
            shares2.append(ele)
    return response.json(dict(shares=shares2))


@auth.requires_signature()
def create_share():
    # Warp the binary data into a file
    stream = io.BytesIO(request.vars.picture.value)
    db.shares.insert(picture=db.shares.picture.store(stream, request.vars.picture.filename),
                     author=auth.user_id,
                     title=request.vars.title,
                     information=request.vars.information,
                     first_name=auth.user.first_name,
                     last_name=auth.user.last_name
                     )
    return response.json(dict())


@auth.requires_login()
def load_messages():
    share_id = long(request.vars.share_id)
    messages = db(db.messages.share_id == share_id).select(orderby=~db.messages.create_time)
    for message in messages:
        message.avatar = db(db.auth_user.id == message.author).select(db.auth_user.avatar).first().avatar
    return response.json(dict(messages=messages))


@auth.requires_signature()
def create_message():
    user_id = auth.user_id
    message_content = request.vars.message_content
    share_id = long(request.vars.share_id)
    db.messages.insert(author=user_id,
                       message_content=message_content,
                       share_id=share_id,
                       first_name=auth.user.first_name,
                       last_name=auth.user.last_name
                       )
    row = db(db.shares.id == share_id).select().first()
    row.create_time = datetime.utcnow()
    row.update_record()
    return response.json(dict())


@auth.requires_login()
def people():
    user_id = long(auth.user_id)
    return dict(user_id=user_id)


@auth.requires_login()
def load_people():
    pattern = request.vars.search.lower()
    number = int(request.vars.number)

    rows = db(db.auth_user).select(db.auth_user.id,
                                   db.auth_user.first_name,
                                   db.auth_user.last_name,
                                   db.auth_user.introduction,
                                   db.auth_user.avatar,
                                   orderby=~db.auth_user.create_time
                                   )
    people = []
    for row in rows:
        temp = {}
        temp['id'] = row.id
        temp['first_name'] = row.first_name
        temp['last_name'] = row.last_name
        temp['introduction'] = row.introduction
        temp['avatar'] = row.avatar
        authorshares = db(db.shares.author == row.id).select(limitby=(0, 3))
        shares = []
        for eachshare in authorshares:
            item = {}
            item['picture'] = eachshare.picture
            shares.append(item)

        temp['shares'] = shares
        if len(people) < number:
            string = temp['first_name'] + ' ' + temp['last_name']
            print string
            string = string.lower()
            if re.search(pattern, string, flags=0):
                people.append(temp)

    return response.json(dict(people=people))


@auth.requires_login()
def artists_shares():
    user_id = long(request.vars.user_id)
    number = long(request.vars.number)
    rows = db(db.shares.author == user_id).select(orderby=~db.shares.create_time)
    return response.json(dict(shares=rows[:number]))


@auth.requires_login()
def profile():
    user_id = long(request.args(0))
    return dict(user_id=user_id)


@auth.requires_login()
def load_profile():
    user_id = long(request.vars.user_id)
    row = db(db.auth_user.id == user_id).select(db.auth_user.introduction,
                                                db.auth_user.address,
                                                db.auth_user.contact_email,
                                                db.auth_user.telephone,
                                                db.auth_user.avatar,
                                                db.auth_user.first_name,
                                                db.auth_user.last_name
                                                ).first()
    return response.json(dict(profile_dict=row))


@auth.requires_signature()
def update_profile():
    user_id = long(request.vars.user_id)
    row = db(db.auth_user.id == user_id).select().first()
    row.introduction = request.vars.introduction
    row.address = request.vars.address
    row.contact_email = request.vars.contact_email
    row.telephone = request.vars.telephone
    row.update_record()
    return response.json(dict(profile_dict=row))


@auth.requires_signature()
def update_avatar():
    user_id = long(request.args(0))
    # Warp the binary data into a file
    stream = io.BytesIO(request.vars.avatar.value)
    # Update the avatar
    row = db(db.auth_user.id == user_id).select().first()
    row.avatar = db.auth_user.avatar.store(stream, request.vars.avatar.filename)
    row.update_record()
    return response.json(dict(profile_dict=row))


@auth.requires_login()
def self_shares():
    user_id = long(request.vars.user_id)
    number = long(request.vars.number)
    rows = db(db.shares.author == user_id).select(orderby=~db.shares.create_time)
    return response.json(dict(shares=rows[:number]))


@auth.requires_signature()
def delete_share():
    share_id = long(request.vars.share_id)
    db(db.shares.id == share_id).delete()
    return response.json(dict())


@auth.requires_signature()
def check_friend():
    friend = long(request.vars.user_id)
    row = db((db.relation.user_id == auth.user_id) & (db.relation.friend == friend)).select().first()
    flag = False
    if row is not None:
        flag = True
    return response.json(dict(flag=flag))


@auth.requires_signature()
def delete_friend():
    friend = long(request.vars.user_id)
    db((db.relation.user_id == auth.user_id) & (db.relation.friend == friend)).delete()
    return response.json(dict())


@auth.requires_signature()
def add_friend():
    friend = long(request.vars.user_id)
    db.relation.insert(user_id=auth.user_id,
                       friend=friend
                       )
    return response.json(dict())


@auth.requires_login()
def load_friends():
    pattern = request.vars.search.lower()
    number = int(request.vars.number)
    user_id = long(request.vars.user_id)
    relations = db(db.relation.user_id == user_id).select(orderby=~db.relation.id)
    rows = []
    for relation in relations:
        row = db(db.auth_user.id == relation.friend).select(db.auth_user.id,
                                                            db.auth_user.first_name,
                                                            db.auth_user.last_name,
                                                            db.auth_user.introduction,
                                                            db.auth_user.avatar,
                                                            orderby=~db.auth_user.create_time
                                                            ).first()
        rows.append(row)
    people = []
    for row in rows:
        if len(people) < number:
            string = row.first_name + ' ' + row.last_name
            string = string.lower()
            if re.search(pattern, string, flags=0):
                people.append(row)
    return response.json(dict(people=people))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    db.auth_user.email.writable = (request.args(0) != 'profile')
    db.auth_user.first_name.writable = (request.args(0) != 'profile')
    db.auth_user.last_name.writable = (request.args(0) != 'profile')
    db.auth_user.introduction.writable = (request.args(0) != 'register')
    db.auth_user.address.writable = (request.args(0) != 'register')
    db.auth_user.contact_email.writable = (request.args(0) != 'register')
    db.auth_user.telephone.writable = (request.args(0) != 'register')

    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def vote():
    shares = db.shares[request.vars.id]
    new_votes = shares.votes + 1
    shares.update_record(votes=new_votes)
    return str(new_votes)
