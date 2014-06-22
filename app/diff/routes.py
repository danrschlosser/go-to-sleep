from flask import Blueprint, abort, request, jsonify
from app.diff.models import Diff
from app.user.models import User
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist
import json

diff = Blueprint('diff', __name__)

FIELDS = set(('time', 'lines_inserted', 'lines_deleted', 'files_changed', 'base_hash', 'remotes'))

@diff.route('/diff/<email>', methods=['POST'])
def new_diff(email):
    try:
        user = User.objects().get(email=email)
    except (MultipleObjectsReturned, DoesNotExist):
        abort(403)

    if not FIELDS.issubset(set(request.form.keys())):
        print FIELDS ^ set(request.form.keys()), request.form.keys()
        abort(400)

    diff_resource = dict((key, request.form[key]) for key in FIELDS)
    fc = diff_resource.get('files_changed')
    diff_resource['files_changed'] = json.loads(diff_resource.get('files_changed'))
    rem = diff_resource.get('remotes')
    diff_resource['remotes'] = json.loads(diff_resource.get('remotes'))
    del diff_resource['remotes']
    diff_resource['user'] = user


    diff = Diff(**diff_resource)
    diff.save()

    user.diffs.append(diff)
    user.save()

    return jsonify(diff.dict())
