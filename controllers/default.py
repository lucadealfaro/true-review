# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

from xml.dom import minidom
from datetime import datetime

#@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()



    logger.info("Here we are, in the controller.")
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))
    """


    #board_list = db().select(db.boards.ALL)

    #board_list = db().select(db.boards.ALL, orderby=~db.boards.last_updated)
    #return dict(board_list=board_list, recent_posts=recent_posts)

    tr_users = db().select(db.tr_user.ALL)
    topic_list = db().select(db.topics.ALL)

    return dict(tr_users=tr_users, topic_list=topic_list)

@auth.requires_login()
def profile():
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user, _class='boardtitle'/login
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
    auth.settings.register_onaccept.append(lambda form: (db.tr_user.insert(author = auth.user_id, joined=datetime.utcnow(), anon=False)) if
                                                             db(db.tr_user.author == auth.user_id).select().first() is None else None
                                        )
    return dict(form=auth())

@auth.requires_login()
def review_paper():
    form = SQLFORM(db.tr_review)
    form.vars.paper = request.args(1)
    paper = db(db.tr_paper.paper_id == request.args(1)).select().first()
    topic = db(db.topics.arxiv_category == request.args(0)).select().first()
    form.vars.paper = paper.id
    if form.process().accepted:
        db.topic_paper_affiliation.update_or_insert(topic=topic.id, paper=paper.id)
        session.flash = T("Added review")
        redirect(URL('default', 'index'))
    return dict(form=form)

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

def reset():
  db(db.posts.id > 0).delete()
  db(db.boards.id > 0).delete()

def paper_list_old():
    my_topic = db.topics(request.args(0))
    if my_topic is None:
        session.flash = T("No such board")
        redirect(URL('default', 'index'))
    list = db().select(db.tr_paper.ALL, orderby=~db.tr_paper.submission_time)
    post_list = []
    '''
    for p in list:
        #if p.board == my_board[0].id:
        if p.topic == my_topic.id:
            post_list.append(p)
    '''
    return dict(paper_list=list)

#paper_list with arxiv implementation
def paper_list():
    my_topic = db.topics(arxiv_category=request.args(0))
    if my_topic is None:
        session.flash = T("No such board")
        redirect(URL('default', 'index'))
    list = db().select(db.tr_paper.ALL, orderby=~db.tr_paper.submission_time)

    return dict(paper_list = list)

def view_paper():
    my_paper = db.tr_paper(request.args(1))
    if my_paper is None:
        session.flash = T("No such paper")
        redirect(URL('default', 'index'))
    review_list = db(db.tr_review.paper == request.args(1)).select()
    return dict(my_paper=my_paper, reviews=review_list)

def view_paper_arxiv():
    import urllib
    url = 'http://export.arxiv.org/api/query?id_list=1512.02162'
    url = 'http://export.arxiv.org/api/query?id_list=' + request.args(1)
    data = urllib.urlopen(url).read()
    #print data

    #here we use minidom from xml.dom to parse the data from the acquired xml
    xmldoc = minidom.parseString(data)
    authlist = xmldoc.getElementsByTagName('name') #returns a list which we can use in the xml

    titles = xmldoc.getElementsByTagName('title')
    #we can print out values from minidom by doing the following
    #print titles[1].childNodes[0].nodeValue
    #titles[0] is the title of the html page, titles[1] is the paper's title

    abstract = xmldoc.getElementsByTagName('summary')
    published = xmldoc.getElementsByTagName('published')

    paper = db(db.tr_paper.paper_id == request.args(1)).select().first()
    review_list = db(db.tr_review.paper == paper.id).select()

    return dict(paper_data=data, authors=authlist, titles=titles, abstract=abstract, published=published,
                reviews=review_list )

def new_paper():
    form = SQLFORM(db.tr_paper)
    papers = db().select(db.tr_paper.ALL)
    if form.process(). accepted:
        '''
        if db((db.topic_paper_affiliation.topic==request.args(0)) &
                (db.topic_paper_affiliation.paper==len(papers))) == 0:
            print 'this is a new paper and it does not have an entry in the intermediate table'
        '''
        session.flash = T("Added paper")
        redirect(URL('default', 'index'))
    return dict(form=form)

#@auth.requires_login()
def new_topics():
    form = SQLFORM(db.topics)
    if form.process(). accepted:
        session.flash = T("Added topic")
        redirect(URL('default', 'index'))
    return dict(form=form)

@auth.requires_login()
@auth.requires_signature()
def new_post():
    # Not necessary but a good idea.
    board = db.boards(request.args(0))
    if board is None:
        session.flash = T("No such board")
        redirect(URL('default', 'index'))
    form = SQLFORM(db.posts)
    now = datetime.utcnow()
    if form.process().accepted:
        form.vars.post_created_on = now
        board.last_updated = now
        board.update_record()
        try:
            db.commit()
        except Exception, e:
            logger.warning("Transaction commit failed while updating board time")
        else:
            session.flash = T("Added post")
            redirect(URL('default', 'posts', args=[request.args(0)]))

    return dict(form=form)

def posts():
    my_board = db.boards(request.args(0))
    if my_board is None:
        session.flash = T("No such board")
        redirect(URL('default', 'index'))
    #my_board = db(db.boards.id == request.args(0)).select()
    pre_post_list = db().select(db.posts.ALL, orderby=~db.posts.post_created_on)
    post_list = []
    for p in pre_post_list:
        #if p.board == my_board[0].id:
        if p.board == my_board.id:
            post_list.append(p)
    edit_button = A('Edit', icon_edit, _href=URL('default', 'edit_post', args=[db.posts.id]))
    return dict(post_list=post_list, my_board=my_board)

@auth.requires_login()
@auth.requires_signature()
def edit_post():
    my_post = db.posts(request.args(0))
    if my_post is None:
        session.flash = T("No such post")
        redirect(URL('default', 'index'))
    form = SQLFORM(db.posts, record=my_post)
    if form.process(). accepted:
        session.flash = T("Post edited")
        redirect(URL('default', 'index'))
    return dict(form=form)

@auth.requires_login()
@auth.requires_signature()
def delete_post():
    db(db.posts.id == request.args(0)).delete()
    session.flash = T("Post deleted")
    redirect(URL('default', 'index'))

def recent_posts(bid):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    pre_post_list = db(db.posts.post_created_on > yesterday).select()
    post_list = []
    for p in pre_post_list:
        if p.board == bid:
            post_list.append(p)
    return len(post_list)
