from flask import Blueprint, abort, request, jsonify
from app.diff.models import Diff
from app.user.models import User
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist

diff = Blueprint('diff', __name__)

FIELDS = set(['time', 'lines_inserted', 'lines_deleted', 'files_changed',
          'base_hash'])

@diff.route('/diff/<email>', methods=['POST'])
def new_diff(email):
    try:
        user = User.objects().get(email=email)
    except (MultipleObjectsReturned, DoesNotExist):
        abort(400)

    if not FIELDS.issubset(request.form.keys()):
        abort(400)

    diff_resource = dict((key, request.form[key]) for key in FIELDS)
    diff_resource['user'] = user

    diff = Diff(**diff_resource)
    diff.save()

    user.diffs.append(diff)
    user.save()

    return jsonify(diff.dict())
