from app import db
from datetime import datetime
from app.repo.models import Repo

class Diff(db.Document):
    """"""
    date_created    = db.DateTimeField(required=True, default=datetime.now)
    time            = db.LongField(required=True)
    lines_inserted  = db.IntField(required=True)
    lines_deleted   = db.IntField(required=True)
    base_hash       = db.StringField(required=True)
    files_changed   = db.ListField(db.StringField())
    remotes         = db.ListField(db.ReferenceField('Repo'))
    user            = db.ReferenceField('User', required=True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['user', 'time']
    }

    @classmethod
    def by_repo_slug(cls, repo_slug, **kwargs):
        repo = Repo.objects().get(slug=repo_slug)
        return Diff.objects(remotes=repo, **kwargs)

    @property
    def email(self):
        return self.user.email

    def __repr__(self):
        return "<Diff %s (id=%s)>" % (self.user.email, self.id)

    def dict(self):
        return {
            'time': self.time,
            'lines_inserted': self.lines_inserted,
            'lines_deleted': self.lines_deleted,
            'files_changed': self.files_changed,
            'base_hash': self.base_hash,
            'email': self.email,
        }
