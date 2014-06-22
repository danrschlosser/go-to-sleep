from app import db
from datetime import datetime
from flask import url_for
from app.diff.models import Diff
from app.active_window.models import ActiveWindow


class User(db.Document):
    """"""
    date_created   = db.DateTimeField(required=True, default=datetime.now)
    name           = db.StringField(required=True, max_length=510)
    email          = db.EmailField(required=True, unique=True)
    diffs          = db.ListField(db.ReferenceField(Diff))
    active_windows = db.ListField(db.ReferenceField(ActiveWindow))

    meta = {
        'allow_inheritance': True,
        'indexes': ['email']
    }

    def percent_inserts(self):
        inserts = sum([diff.lines_inserted for diff in self.diffs])
        deletes = sum([diff.lines_deleted for diff in self.diffs])
        if inserts + deletes == 0:
            return 50
        i_p = float(inserts)/(inserts+deletes)*100
        return i_p

    def percent_deletes(self):
        inserts = sum([diff.lines_inserted for diff in self.diffs])
        deletes = sum([diff.lines_deleted for diff in self.diffs])
        if inserts + deletes == 0:
            return 50
        d_p = float(deletes)/(inserts+deletes)*100
        return d_p

    @property
    def diffs_count(self):
        return len(self.diffs)

    @property
    def url(self):
        return url_for('user.single_user', email=self.email, _external=True)

    def __repr__(self):
        return "<User %s (id=%s)>" % (self.email, self.id)

    def dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'url': self.url,
            'diffs_count': self.diffs_count
        }
