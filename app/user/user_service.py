from app.user.models import User
from flask import url_for
import requests

API_URL ='https://api.github.com/users/%s'

def new_user(email, username):
    resp = requests.get(API_URL % username)
    name = resp.json()['name']
    url  = url_for('user.single_user', username=username, _external=True)
    user = User(email=email, username=username, name=name, url=url)
    user.save()
    return user
