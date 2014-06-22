from app import db
from datetime import datetime
from flask import url_for

class User(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=datetime.now)
    name = db.StringField(required=True, max_length=510)
    email = db.EmailField(required=True, unique=True)
    diffs = db.ListField(db.ReferenceField('Diff'))

    meta = {
        'allow_inheritance': True,
        'indexes': ['email']
    }

    @property
    def url(self):
        return url_for('user.single_user', email=self.email, _external=True)

    def clean(self):
        """Update date_modified."""
        self.date_modified = datetime.now()

    def __repr__(self):
        return "<User %s (id=%s)>" % (self.username, self.id)

    def dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'username': self.username,
            'url': self.url
        }
