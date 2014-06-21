from flask import Blueprint, abort, jsonify, url_for, redirect
from app.user.models import User
from app.user.user_service import new_user

user = Blueprint('user', __name__)

@user.route('/user/<username>', methods=['GET'])
def single_user(username):
    if User.objects(username=username).count() != 1:
        abort(404)
    user = User.objects().get(username=username)
    return jsonify(user.dict())

@user.route('/users', methods=['GET'])
def users():
    """All users DEV ONLY"""
    return jsonify({"users": [user.dict() for user in User.objects()]})


@user.route('/users/create/<email>/<username>', methods=['POST'])
def create_user(email, username):
    if User.objects(email=email).count() != 0:
        abort(400)
    user = new_user(email, username)
    resp = {
        'user': {
            'email': user.email,
            'name': user.name,
            'username': user.username,
            'url': user.url
        }
    }
    return jsonify(resp)


@user.route('/users/wipe', methods=['GET'])
def wipe_users():
    for user in User.objects():
        user.delete()
    return redirect(url_for('.users'))