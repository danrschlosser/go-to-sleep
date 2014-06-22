from flask import Blueprint, abort, jsonify, url_for, redirect, render_template, request
from app.user.models import User
from app.diff.models import Diff
from datetime import datetime, timedelta, date
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist, NotUniqueError
import json
from bson import ObjectId
import pymongo

MAGIC = 0.20
MAGIC2 = 100

user = Blueprint('user', __name__)
client = pymongo.MongoClient()


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
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
    dbwindow = db.active_window

    query = {
        'user': user['id'],
    }

    if 'after' in request.args or 'before' in request.args:
        query['time'] = {}
        if 'after' in request.args:
            query['time']['$gte'] = long(request.args['after'])
        if 'before' in request.args:
            query['time']['$lte'] = long(request.args['before'])

    derped = list(dbdiff.find(query))
    derped2 = list(dbwindow.find(query))

    return render_template('user.html', userRaw=user.dict(), user=json.dumps(user.dict()), diffs=json.dumps(derped, cls=MongoJsonEncoder), actWindows=json.dumps(derped2, cls=MongoJsonEncoder))

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

    print email, name
    print User.objects()
    print User.objects(email=email)
    print User.objects().get(email=email)

    try:
        user = User.objects().get(email=email)
    except DoesNotExist:
        user = User(email=email, name=name)
        user.save()
    except MultipleObjectsReturned:
        abort(500)
    except NotUniqueError:
        abort(203)

    resp = {'user': user.dict()}
    return jsonify(resp)

@user.route('/users/wipe', methods=['GET'])
def wipe_users():
    for user in User.objects():
        user.delete()
    return redirect(url_for('.users'))

@user.route('/go-to-sleep/<email>', methods=['GET'])
def check_if_fit_for_sleep(email):
    try:
      user = User.objects().get(email=email)
      current_time = long(datetime.now().strftime('%s'))
      param_60_mva = {
          'user': user['id'],
          'time': {'$lte': current_time},
          'time': {'$gte': long((datetime.now() - timedelta(seconds=60*60)).strftime('%s'))},
      }
      param_10_mva = {
          'user': user['id'],
          'time': {'$lte': current_time},
          'time': {'$gte': long((datetime.now() - timedelta(seconds=10*60)).strftime('%s'))},
      }

      db = client.cloakedhipster
      dbdiff = db.diff

      hour_records = list(dbdiff.find(param_60_mva))
      ten_min_records = list(dbdiff.find(param_10_mva))

      hour_mva = 1.0 * sum((
          x['lines_inserted'] + x['lines_deleted']
          for x in hour_records
          if x['lines_inserted'] + x['lines_deleted'] < MAGIC2)
      ) / len(hour_records)
      ten_mva = 1.0 * sum(
          (x['lines_inserted'] + x['lines_deleted']
          for x in ten_min_records
          if x['lines_inserted'] + x['lines_deleted'] < MAGIC2)
      ) / len(ten_min_records)

      print 'hour:{}, ten_minutes:{}'.format(hour_mva, ten_mva)

      if hour_mva * MAGIC > ten_mva:
          return json.dumps({'outcome': True})

      return json.dumps({'outcome': False})
    except DoesNotExist:
      abort(403)
