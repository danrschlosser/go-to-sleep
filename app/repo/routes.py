from flask import Blueprint, abort, jsonify, request, render_template
from app.repo.models import Repo
from app.diff.models import Diff
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist
import pymongo
from bson.objectid import ObjectId
import json
import datetime

repo = Blueprint('repo', __name__)

client = pymongo.MongoClient()


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)

@repo.route('/api/repo/<repo_slug>')
def get_by_repo(repo_slug):
    derped = {'diffs': [d.dict() for d in Diff.by_repo_slug(repo_slug, **request.args)]}
    return jsonify(derped)

@repo.route('/repo/<slug>')
def single_repo(slug):
    try:
        db = client.cloakedhipster
        dbdiff = db.diff
        dbrepo = db.repo

        repo = dbrepo.find({'slug': slug})[0]
        """
        repo = Repo.objects.get(slug=slug)
        args = {
            k: v[0] for (k, v) in request.args.items()
        }
        objs = Diff.by_repo_slug(slug, **args)
        t2 = timeit.default_timer()
        derped = {'diffs': [d.dict() for d in objs]}
        t3 = timeit.default_timer()
        """

        query = {
            'remotes': repo['_id'],
        }
        if 'after' in request.args or 'before' in request.args:
            query['time'] = {}
            print request.args['after']
            if 'after' in request.args:
                query['time']['$gte'] = long(request.args['after'])
            if 'before' in request.args:
                query['time']['$lte'] = long(request.args['before'])

        derped = list(dbdiff.find(query))
        print 'fetched: {}'.format(len(derped)),

        return render_template("repo.html", repo=repo, diffs=json.dumps(derped, cls=MongoJsonEncoder))
    except (MultipleObjectsReturned, DoesNotExist):
        abort(400)

@repo.route('/repo/create', methods=['POST'])
def create_repo():
    name = request.form.get('name')
    slug = request.form.get('slug')

    if not name or not slug:
        abort(400)

    try:
        repo = Repo.objects().get(slug=slug)
    except DoesNotExist:
        repo = Repo(name=name, slug=slug)
        repo.save()
    except MultipleObjectsReturned:
        abort(500)

    resp = {'repo': repo.dict()}
    return jsonify(resp)