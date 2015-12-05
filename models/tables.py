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

db.define_table('tr_reviewer',
                Field('reputation', 'float'),
                Field('num_reviewed', 'integer'),
                Field('topic' 'reference topics'),
)

#many to many relationship between users and reviewers
db.define_table('user_reviewer_affiliation',
                Field('user', 'reference tr_user'),
                Field('reviewer', 'reference tr_reviewer'),
)


db.define_table('topics',
                Field('name'),
                #Field('subtopic')
                )


#many to many relationship between topics and papers
db.define_table('topic_paper_affiliation',
                Field('topic', 'reference topics'),
                Field('paper' 'reference tr_paper'),
                )

db.define_table('tr_review',
                Field('review_content', 'text'),
                Field('score', 'float'),
                Field('review_time', 'datetime'),
                Field('score_before', 'float'),
                Field('paper', 'reference tr_paper'),
                Field('paper content', 'reference tr_paper_content')
                )
db.tr_review.review_time.default = datetime.utcnow()


#many to many between reviewer(s) and reviews
db.define_table('reviewer_review_affiliation',
                Field('reviewer', 'reference tr_reviewer'),
                Field('review', 'reference tr_review'),
                )


#
db.define_table('tr_paper',
                Field('title'),
                Field('author'), # Ok. Later perhaps we can link papers to authors who are also reviewers.
                #Field('topic', 'reference topics'),

                Field('submission_time', 'datetime'),
                Field('abstract', 'text'),
                Field('summary', 'text'),
                # We cache some quantities.
                Field('avg_quality', 'float'),
                Field('num_reviews', 'integer'),
                )
db.papers.submission_time.default = datetime.utcnow()


db.define_table('tr_paper_content',
                Field('content', 'text'),
                Field('version', 'integer'),
                Field('paper_title', 'reference tr_paper'),
              #  Field('date', 'text'),
)


db.papers.topic.default = request.args(0)
db.papers.topic.writable = False
db.papers.submission_time.writable = False




#db.messages.board.readable = db.messages.board.writable = False




