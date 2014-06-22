from app import db
from datetime import datetime

class ActiveWindow(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=datetime.now)
    time         = db.LongField(required=True)
    app          = db.StringField(required=True)
    title        = db.StringField(required=True)
    user         = db.ReferenceField('User', required=True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['user', 'time', 'app',]
    }

    def __repr__(self):
        return "<ActiveWindow %s (id=%s)>" % (self.title, self.id)

    def dict(self):
        return {
            'time': self.time,
            'app': self.app,
            'title': self.title,
            'user': self.user.email
        }
