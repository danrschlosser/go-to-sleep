from app import db
from datetime import datetime
from flask import url_for
from app.diff.models import Diff
from app.active_window.models import ActiveWindow
import pymongo

client = pymongo.MongoClient()


class User(db.Document):
    """"""
    date_created   = db.DateTimeField(required=True, default=datetime.now)
    name           = db.StringField(required=True, max_length=510)
    email          = db.EmailField(required=True, unique=True)
    should_sleep   = db.BooleanField(default=False)
    diffs          = db.ListField(db.ReferenceField(Diff))
    active_windows = db.ListField(db.ReferenceField(ActiveWindow))

    meta = {
        'allow_inheritance': True,
        'indexes': ['email']
    }

    def clean(self):
        try :
            if self.should_sleep is None:
                self.should_sleep = True
        except AttributeError:
            self.should_sleep = True

    def percent_inserts(self):
        db = client.cloakedhipster
        dbdiff = db.diff
        diffs = dbdiff.find({
          'user': self['id']
        })

        inserts = 0
        deletes = 0
        for diff in diffs:
            try:
                inserts += diff['lines_inserted']
                deletes += diff['lines_deleted']
            except KeyError:
                pass

        if inserts + deletes == 0:
            return 50
        i_p = float(inserts)/(inserts+deletes)*100
        return i_p

    def percent_deletes(self):
        db = client.cloakedhipster
        dbdiff = db.diff
        diffs = dbdiff.find({
          'user': self['id']
        })

        inserts = 0
        deletes = 0
        for diff in diffs:
            try:
                inserts += diff['lines_inserted']
                deletes += diff['lines_deleted']
            except KeyError:
                pass

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
            'diffs_count': self.diffs_count,
            'should_sleep': self.should_sleep
        }
