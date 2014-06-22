from flask import Blueprint, abort, jsonify, url_for, redirect, render_template, request
from app.user.models import User
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist

user = Blueprint('user', __name__)

@user.route('/user/<email>', methods=['GET'])
def single_user(email):
    if User.objects(email=email).count() != 1:
        abort(404)
    user = User.objects().get(email=email)
    return render_template('user.html', user=user)

@user.route('/users', methods=['GET'])
def users():
    """All users DEV ONLY"""
    return jsonify({"users": [user.dict() for user in User.objects()]})

@user.route('/users/create', methods=['POST'])
def create_user():
    if 'email' not in request.form or 'name' not in request.form:
        abort(400)

    email = request.form['email']
    name = request.form['name']

    try:
        user = User.objects().get(email=email)
    except DoesNotExist:
        user = User(email=email, name=name)
        user.save()
    except MultipleObjectsReturned:
        abort(400)

    resp = {
        'user': user.dict()
    }
    return jsonify(resp)

@user.route('/users/wipe', methods=['GET'])
def wipe_users():
    for user in User.objects():
        user.delete()
    return redirect(url_for('.users'))
