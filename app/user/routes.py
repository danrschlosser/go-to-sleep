from flask import Blueprint, abort, jsonify, url_for, redirect, render_template, request
from app.user.models import User
from app.diff.models import Diff
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist
import json
from bson import ObjectId
import pymongo
import datetime

user = Blueprint('user', __name__)
client = pymongo.MongoClient()


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)

@user.route('/user/<email>', methods=['GET'])
def single_user(email):
    if User.objects(email=email).count() != 1:
        abort(404)
    user = User.objects().get(email=email)
    """
    args = {
        k: v[0] for (k, v) in request.args.items()
    }
    """
    db = client.cloakedhipster
    dbdiff = db.diff

    query = {
        'user': user['id'],
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

    #objs = Diff.objects(user=user, **args)
    #derped = {'diffs': [d.dict() for d in objs]}
    return render_template('user.html', user=user, diffs=json.dumps(derped, cls=MongoJsonEncoder))

@user.route('/users', methods=['GET'])
def users():
    """All users DEV ONLY"""
    return jsonify({"users": [user.dict() for user in User.objects()]})

@user.route('/users/create', methods=['POST'])
def create_user():
    email = request.form.get('email')
    name = request.form.get('name')

    if not email or not name:
        abort(400)

    try:
        user = User.objects().get(email=email)
    except DoesNotExist:
        user = User(email=email, name=name)
        user.save()
    except MultipleObjectsReturned:
        abort(500)

    resp = {'user': user.dict()}
    return jsonify(resp)

@user.route('/users/wipe', methods=['GET'])
def wipe_users():
    for user in User.objects():
        user.delete()
    return redirect(url_for('.users'))
