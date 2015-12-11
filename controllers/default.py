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
import json
import urllib

#@auth.requires_login()
def index():
    tr_users = db().select(db.tr_user.ALL)
    topic_list = db().select(db.topics.ALL)

    #Create an sqlform grid
    links = [dict(header='View Paper',
                 body = lambda r: A(icon_paper, '    Papers', _class='btn btn-primary',
                                    _href=URL('default', 'paper_list', args=[r.arxiv_category])))]

    q = db.topics
    grid = SQLFORM.grid(q,
                        links=links,
                        )

    return dict(tr_users=tr_users, topic_list=topic_list, grid=grid)

@auth.requires_login()
def profile():
    return dict()

@auth.requires_login()
def discussions():
    return dict()

def user():

    #if the user is new they must be put into the tr_user table
    auth.settings.register_onaccept.append(lambda form: (db.tr_user.insert(author = auth.user_id, joined=datetime.utcnow(), anon=False)) if
                                                             db(db.tr_user.author == auth.user_id).select().first() is None else None
                                        )
    return dict(form=auth())

#page for paper reviews
@auth.requires_login()
def review_paper():
    form = SQLFORM(db.tr_review)
    form.vars.paper = request.args(1)
    paper = db(db.tr_paper.paper_id == request.args(1)).select().first()
    topic = db(db.topics.arxiv_category == request.args(0)).select().first()
    form.vars.paper = paper.id
    curr_tr_user = db.tr_user(author=auth.user_id)
    if form.process(onvalidation=assign).accepted:
        db(db.tr_paper.paper_id == request.args(1)).update(num_reviews=db.tr_paper.num_reviews + 1)
        avg_score()
        session.flash = T("Added review")
        redirect(URL('default', 'index'))
    return dict(form=form)

def avg_score():
    paper = db(db.tr_paper.paper_id == request.args(1)).select().first()
    review_list = db(db.tr_review.paper == paper.id).select()
    print paper
    print review_list
    sum = 0
    for review in review_list:
       sum += review.score
    print sum

    if paper.num_reviews == 0:
        avg_score = 0
        db(db.tr_paper.paper_id == request.args(1)).update(avg_quality=avg_score)
    else:
        avg_score = (sum/paper.num_reviews)
        print paper.num_reviews
        db(db.tr_paper.paper_id == request.args(1)).update(avg_quality=avg_score)

    print avg_score
    print db(db.tr_paper.paper_id == request.args(1)).select().first().avg_quality

#assigns the reviewer to the review if the form is accepted
def assign(form):
    paper = db(db.tr_paper.paper_id == request.args(1)).select().first()
    curr_tr_user = db.tr_user(author=auth.user_id)
    topic = db(db.topics.arxiv_category == request.args(0)).select().first()
    #add the paper to the current topic if not already in the relation table
    db.topic_paper_affiliation.update_or_insert(topic=topic.id, paper=paper.id)
    #make the current user a reviewer for this topic if they are not already one
    #if the current reviewer and review are not in the tables
    if db.tr_reviewer(topic=topic.id, tr_user=curr_tr_user.id) is None:
        db.tr_reviewer.insert(reputation=0, num_reviewed=1, topic=topic.id, tr_user=curr_tr_user.id)
    this_reviewer = db.tr_reviewer(topic=topic.id, tr_user=curr_tr_user.id)
    #finally add the current reviewer id to the paper
    form.vars.reviewer = this_reviewer


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

#paper_list with arxiv implementation
def paper_list():
    my_topic = db.topics(arxiv_category=request.args(0))
    if my_topic is None:
        session.flash = T("No such board")
        redirect(URL('default', 'index'))
    ##########
    my_id = my_topic.id
    print my_id
    #check if there are no papers in the paper list
    list = db(db.topic_paper_affiliation.topic == my_id).select()
    list3 = []
    print list
    if list.first() is None:
        return dict(paper_list=[])
    else:
        topic_and_paper = db((db.topics.id==db.topic_paper_affiliation.topic)  & (db.tr_paper.id==db.topic_paper_affiliation.paper))
        for row in topic_and_paper(db.topics.id==my_topic.id).select():
            #print row.tr_paper.title
            list3.append(row.tr_paper)
    return dict(paper_list=list3)

def view_paper():
    my_paper = db.tr_paper(request.args(1))
    if my_paper is None:
        session.flash = T("No such paper")
        redirect(URL('default', 'index'))
    review_list = db(db.tr_review.paper == request.args(1)).select()
    return dict(my_paper=my_paper, reviews=review_list)


def view_paper_arxiv():
    my_paper = db.tr_paper(paper_id = request.args(1))
    url = 'http://export.arxiv.org/api/query?id_list=1512.02162'
    url = 'http://export.arxiv.org/api/query?id_list=' + request.args(1)
    print url + '*********************************'
    data = urllib.urlopen(url).read()

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
    print "***"
    print paper
    print "***"
    review_list = db(db.tr_review.paper == paper.id).select()
    print review_list
    has_reviewed = False
    for r in review_list:
        if r.auth_reviewer == auth.user_id:
            has_reviewed = True
    print len(review_list)
    return dict(paper_data=data, authors=authlist, titles=titles, abstract=abstract, published=published,
                reviews=review_list, has_reviewed=has_reviewed, my_paper=my_paper )

def new_paper():
    form = SQLFORM(db.tr_paper)
    topic = db(db.topics.arxiv_category == request.args(0)).select().first()
    papers = db().select(db.tr_paper.ALL)
    if form.process(). accepted:
        '''
        if db((db.topic_paper_affiliation.topic==request.args(0)) &
                (db.topic_paper_affiliation.paper==len(papers))) == 0:
            print 'this is a new paper and it does not have an entry in the intermediate table'
        '''
        #add the paper to the current topic if not already in the relation table
        db.topic_paper_affiliation.update_or_insert(topic=topic.id, paper=form.vars.id)
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

@auth.requires_signature()
def add_msg():
    db.post.update_or_insert((db.post.message_id == request.vars.msg_id),
            message_id=request.vars.msg_id,
            message_content=request.vars.msg,
            is_draft=json.loads(request.vars.is_draft))
    return "ok"

@auth.requires_signature()
def add_board():
    db.boards.update_or_insert((db.boards.board_id == request.vars.msg_id),
            board_id=request.vars.msg_id,
            name=request.vars.title,
            description=request.vars.msg,
            editable=json.loads(request.vars.is_draft),
            board_topic=request.args(0)
    )
    return "ok"

def get_boards():
    rows=db().select(db.boards.ALL)
    rows=db(db.boards.board_topic == request.args(0)).select()
    board_list = [dict(name=r.name, description=r.description, editable=r.editable, board_id=r.board_id) for r in rows]
    return response.json(dict(msg_dict = board_list))