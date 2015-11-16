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

Auth(db)
## after auth = Auth(db)
auth.settings.extra_fields['auth_user']= [
  Field('address'),
  Field('city'),
  Field('zip'),
  Field('phone')]
## before auth.define_tables(username=True)
auth.define_tables(username=True)

db.define_table('tr_user',
                Field('user_id', db.auth_user),
                Field('name'),
                Field('joined', 'datetime'),
                Field('bio', 'text'),
                Field('email'),
                Field('user_active', 'boolean'),
                Field('on_top_page', 'boolean')
                )
db.tr_user.joined.default = datetime.utcnow()
db.tr_user.joined.readable = db.tr_user.joined.writable = False



#db.messages.board.readable = db.messages.board.writable = False




