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
                Field('user_id', db.auth_user),
                Field('name'),
                Field('joined', 'datetime'),
                #Field('bio', 'text'),
                Field('email'),
               # Field('topic', 'reference topics')
                #Field('user_active', 'boolean'),
                #Field('on_top_page', 'boolean')
                )
db.tr_user.joined.default = datetime.utcnow()
db.tr_user.joined.readable = db.tr_user.joined.writable = False

db.define_table('topics',
                Field('name'),
                Field('arxiv_category')
                )

db.define_table('tr_reviewer',
                Field('reputation', 'float'),
                Field('num_reviewed', 'integer'),
                Field('topic', 'reference topics'),
)

#many to many relationship between users and reviewers
db.define_table('user_reviewer_affiliation',
                Field('review_user', 'reference tr_user'),
                Field('reviewer', 'reference tr_reviewer'),
)

#
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


db.define_table('tr_paper_content',
                Field('paper_content', 'text'),
                Field('paper_version', 'integer'),
                Field('paper_title', 'reference tr_paper'),
              #  Field('date', 'text'),
)


db.define_table('tr_review',
                Field('review_content', 'text'),
                Field('score', 'float'),
                Field('review_time', 'datetime'),
                Field('score_before', 'float'),
                Field('paper', 'reference tr_paper'),
                #Field('paper_content', 'reference tr_paper_content') #causing problems in debug, to add later
                )
db.tr_review.review_time.default = datetime.utcnow()
db.tr_review.review_time.writable = db.tr_review.paper.writable = False
db.tr_review.score_before.readable = db.tr_review.score_before.writable = False
db.tr_review.score_before.default = 0
db.tr_review.paper.default = request.args(1)
#db.tr_review.paper_content.writable = False
#db.tr_review.paper_content.default = request.args(1)



#many to many between reviewer(s) and reviews
db.define_table('reviewer_review_affiliation',
                Field('reviewer', 'reference tr_reviewer'),
                Field('review', 'reference tr_review'),
                )


#many to many relationship between topics and papers
db.define_table('topic_paper_affiliation',
                Field('topic', 'reference topics'),
                Field('paper', 'reference tr_paper'),
                )

#db.messages.board.readable = db.messages.board.writable = False




