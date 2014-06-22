from app import db
from datetime import datetime

class Diff(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=datetime.now)
    time = db.LongField(required=True)
    lines_inserted = db.IntegerField(required=True)
    lines_deleted = db.IntegerField(required=True)
    files_changed = db.ListField(db.StringField())
    base_hash = db.StringField(required=True)
    user = db.ReferenceField('User', required=True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['user', 'time']
    }

    @property
    def email(self):
        return self.user.email

    def clean(self):
        """Update date_modified."""
        self.date_modified = datetime.now()

    def __repr__(self):
        return "<User %s (id=%s)>" % (self.username, self.id)

    def dict(self):
        return {
            'time': self.time,
            'lines_inserted': self.lines_inserted,
            'lines_deleted': self.lines_deleted,
            'files_changed': self.files_changed,
            'base_hash': self.base_hash,
            'email': self.email
        }
