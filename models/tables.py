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

db.define_table('topics',
                Field('name'),
                Field('subtopic')
                )

# Is this a user, or a user for a single topic?  Seems more like a user, but then we need 
# a many to many relation to topics that includes also the reputation of the user for that topic.
db.define_table('tr_user',
                Field('user_id', db.auth_user),
                Field('name'),
                Field('joined', 'datetime'),
                #Field('bio', 'text'),
                Field('email'),
                Field('topic', 'reference topics')
                #Field('user_active', 'boolean'),
                #Field('on_top_page', 'boolean')
                )
db.tr_user.joined.default = datetime.utcnow()
db.tr_user.joined.readable = db.tr_user.joined.writable = False


#
db.define_table('papers',
                Field('title'),
                Field('author'), # Ok. Later perhaps we can link papers to authors who are also reviewers.
                Field('topic', 'reference topics'),
                Field('submission_time', 'datetime'),
                Field('abstract', 'text'),
                Field('summary', 'text'),
                # We cache some quantities.
                Field('avg_quality', 'float'),
                Field('num_reviews', 'integer'),
                )

db.papers.submission_time.default = datetime.utcnow()
db.papers.topic.default = request.args(0)
db.papers.topic.writable = False
db.papers.submission_time.writable = False

db.define_table('reviews',
                Field('creation_date', 'datetime', default=datetime.utcnow()),
                Field('reviewer', 'reference tr_user'),
                Field('grade', 'float'),
                Field('review_content', 'text'),
                Field('paper', 'reference papers'),
                )

#db.messages.board.readable = db.messages.board.writable = False




