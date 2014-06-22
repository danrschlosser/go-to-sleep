from app import db
from datetime import datetime
from flask import url_for

class Repo(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=datetime.now)
    contributors = db.ListField(db.ReferenceField('User'))
    name         = db.StringField(required=True)
    slug         = db.StringField(required=True, unique=True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['contributors']
    }

    @property
    def url(self):
        return url_for('repo.single_repo', slug=self.slug)

    def __repr__(self):
        return "<Repo %s (id=%s)>" % (self.username, self.id)

    def dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'contributors': self.contributors
        }
