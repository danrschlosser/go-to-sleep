from app import db
from datetime import datetime;

class User(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=datetime.now)
    name = db.StringField(required=True, max_length=510)
    username = db.StringField(required=True, max_length=510, unique=True)
    email = db.EmailField(required=True, unique=True)
    url = db.URLField(required=True, unique=True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['email']
    }

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