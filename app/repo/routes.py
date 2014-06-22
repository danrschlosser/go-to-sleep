from flask import Blueprint, abort, jsonify, request, render_template
from app.repo.models import Repo
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist

repo = Blueprint('repo', __name__)

@repo.route('/repo/<slug>')
def single_repo(slug):
    try:
        repo = Repo.objects.get(slug=slug)
    except (MultipleObjectsReturned, DoesNotExist):
        abort(400)
    return render_template("repo.html", repo=repo)

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