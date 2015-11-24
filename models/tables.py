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

textdb = DAL('sqlite://storage.db')

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



db.define_table('papers',
                Field('title'),
                Field('author'), # Ok. Later perhaps we can link papers to authors who are also reviewers.
                Field('topic', 'reference topics'),
                Field('abstract', 'text'),
                Field('summary', 'text'),
                # We cache some quantities.
                Field('avg_quality', 'float'),
                Field('num_reviews', 'integer'),
                )

db.define_table('reviews',
                Field('creation_date', 'datetime', default=datetime.utcnow()),
                Field('reviewer', 'reference tr_user'),
                Field('grade', 'float'),
                Field('review_content', 'text'),
                Field('paper', 'reference papers'),
                )


textdb.define_table('long_text',
                # Luca says: just have one field called "textcontent" or something like that.
                Field('abstract', 'text'),
                Field('summary', 'text'),
                Field('review', 'text')
                )

db.papers.abstract.represent = lambda v, r: textdb.long_text(v).abstract
db.papers.summary.represent = lambda v, r: textdb.long_text(v).summary
db.reviews.review_content.represent = lambda v, r: textdb.long_text(v).review_content

# This should go in a controller. 
def edit():
    r = db.mytable(request.args(0))
    old_text_id = int(r.mytext) if r is not None else None
    form = SQLFORM(record=r)
    #if form.process(onvalidation=my_validator(old_text_id)).accepted:
        #redirect(wherever)
    return dict(form=form)

db.define_table('mytable',
    Field('mytext', 'text'),
)

textdb.define_table('texttable',
    Field('textval', 'text')
)

db.mytable.mytext.represent = lambda v, r: textdb.texttable(v).textval


def my_validator(old_text_id):
    def validate(form):
        if old_text_id is None:
            # We need to insert.
            i = textdb.texttable.insert(textval = form.vars.mytext)
            form.vars.mytext = str(i)
        else:
            # We need to replace.
            textdb(textdb.texttable.id == int(old_text_id)).update(textval = form.vars.mytext)
            form.vars.mytext = str(old_text_id)
        return form


def edit():
    r = db.mytable(request.args(0))
    old_text_id = int(r.mytext) if r is not None else None
    form = SQLFORM(record=r)
    #if form.process(onvalidation=my_validator(old_text_id)).accepted:
        #redirect(wherever)
    return dict(form=form)

################### end comment out


#db.messages.board.readable = db.messages.board.writable = False




