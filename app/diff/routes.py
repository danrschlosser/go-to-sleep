from flask import Blueprint, abort, request, jsonify
from app.diff.models import Diff
from app.user.models import User
from app.repo.models import Repo
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist
import json
import re

diff = Blueprint('diff', __name__)

FIELDS = {'time', 'lines_inserted', 'lines_deleted', 'files_changed', 'base_hash', 'remotes'}

@diff.route('/diff/<email>', methods=['POST'])
def new_diff(email):
    try:
        user = User.objects().get(email=email)
    except (MultipleObjectsReturned, DoesNotExist):
        abort(403)

    if not FIELDS.issubset(set(request.form.keys())):
        abort(400)

    diff_resource = dict((key, request.form[key]) for key in FIELDS)
    fc = diff_resource.get('files_changed')
    diff_resource['files_changed'] = json.loads(fc)
    rem = diff_resource.get('remotes')

    repo_re = re.compile(r'(\w+://)?(.+@)*([\w\d\.]+)(:[\d]+)?/*:?(.*)/(.*).git')

    diff_resource['remotes'] = []
    for remote_url in json.loads(rem):
        matches = repo_re.match(remote_url)
        repo_url = '{}:{}'.format(matches.group(5), matches.group(6))
        repo_username = matches.group(6)
        try:
            repo = Repo.objects().get(slug=repo_url)
        except DoesNotExist:
            repo = Repo(name=repo_username, slug=repo_url)
            repo.save()
        except MultipleObjectsReturned:
            abort(500)

        diff_resource['remotes'].append(repo)

    diff_resource['user'] = user

    diff = Diff(**diff_resource)
    diff.save()

    user.diffs.append(diff)
    user.save()

    return jsonify(diff.dict())
