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

from datetime import datetime

# Is this a user, or a user for a single topic?  Seems more like a user, but then we need
# a many to many relation to topics that includes also the reputation of the user for that topic.
db.define_table('tr_user',
                Field('author', db.auth_user, default=auth.user_id),
                #Field('name'),
                Field('joined', 'datetime'),
                #Field('bio', 'text'),
                #Field('email'),
                Field('anon', 'boolean', default=False),
                #Field('topic', 'reference topics')
                Field('user_active', 'boolean', default=True),
                #Field('on_top_page', 'boolean')
                )
db.tr_user.joined.default = datetime.utcnow()
db.tr_user.joined.readable = db.tr_user.joined.writable = False

#data for a topic. User can specify a name and arxiv category
db.define_table('topics',
                Field('name'),
                Field('arxiv_category')
                )

#a reviewer for a topic. a tr_user can have many of these
db.define_table('tr_reviewer',
                Field('reputation', 'float'),
                Field('num_reviewed', 'integer'),
                Field('topic', 'reference topics'),
                Field('tr_user', 'reference tr_user')
)

#many to many relationship between users and reviewers
#### NOT USED ANYMORE SINCE THE RELATION IS ONE TO MANY
db.define_table('user_reviewer_affiliation',
                Field('review_user', 'reference tr_user'),
                Field('reviewer', 'reference tr_reviewer'),
)

#data needed for a paper
db.define_table('tr_paper',
                Field('title'),
                Field('author'), # Ok. Later perhaps we can link papers to authors who are also reviewers.
                #Field('topic', 'reference topics'),
                Field('submission_time', 'datetime'),#change to arxiv submit date
                Field('abstract', 'text'), #remove later? same as summary
                Field('summary', 'text'),
                # We cache some quantities.
                Field('avg_quality', 'float'),
                Field('num_reviews', 'integer'),
                Field('paper_id')
                )
db.tr_paper.submission_time.default = datetime.utcnow()
db.tr_paper.submission_time.writable = False
db.tr_paper.author.readable = db.tr_paper.abstract.readable = db.tr_paper.summary.readable = \
        db.tr_paper.avg_quality.readable = db.tr_paper.num_reviews.readable = False
db.tr_paper.author.writable = db.tr_paper.abstract.writable = db.tr_paper.summary.writable = \
        db.tr_paper.avg_quality.writable = db.tr_paper.num_reviews.writable = False
db.tr_paper.avg_quality.default = 0
db.tr_paper.num_reviews.default = 0

#this table is to keep track of the version of each paper
db.define_table('tr_paper_content',
                Field('paper_content', 'text'),
                Field('paper_version', 'integer'),
                Field('paper_title', 'reference tr_paper'),
              #  Field('date', 'text'),
)

#this is for each review of a paper
db.define_table('tr_review',
                Field('review_content', 'text', requires=IS_LENGTH(minsize=100)),
                Field('score', 'float'),
                Field('review_time', 'datetime'),
                Field('score_before', 'float'),
                Field('paper', 'reference tr_paper'),
                Field('reviewer', 'reference tr_reviewer'),
                Field('auth_reviewer', db.auth_user, default=auth.user_id)
                #Field('paper_content', 'reference tr_paper_content') #causing problems in debug, to add later
                )
db.tr_review.review_time.default = datetime.utcnow()
db.tr_review.review_time.writable = db.tr_review.paper.writable = False
db.tr_review.score_before.readable = db.tr_review.score_before.writable = False
db.tr_review.reviewer.readable = db.tr_review.reviewer.writable = False
db.tr_review.score_before.default = 0
db.tr_review.paper.default = request.args(1)
db.tr_review.auth_reviewer.readable = db.tr_review.auth_reviewer.writable = False
db.tr_review.reviewer.writable = False
db.tr_review.score.requires = IS_INT_IN_RANGE(1, 11)

#db.tr_review.paper_content.writable = False
#db.tr_review.paper_content.default = request.args(1)



#many to many between reviewer(s) and reviews
### NOT USED SINCE RELATION IS ONE TO MANY
db.define_table('reviewer_review_affiliation',
                Field('reviewer', 'reference tr_reviewer'),
                Field('review', 'reference tr_review'),
                )


#many to many relationship between topics and papers
db.define_table('topic_paper_affiliation',
                Field('topic', 'reference topics'),
                Field('paper', 'reference tr_paper'),
                )

db.define_table('boards',
                Field('name'),
                Field('author', db.auth_user, default=auth.user_id),
                Field('last_updated', 'datetime'),
                Field('description', 'text'),
                Field('editable', 'boolean', default=False),
                Field('board_id'),
                Field('board_topic', 'reference topics')
                )
db.boards.last_updated.default = datetime.utcnow()
db.boards.last_updated.readable = db.boards.last_updated.writable = False




