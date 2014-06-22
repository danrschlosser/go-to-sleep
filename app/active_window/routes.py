import json
from flask import Blueprint, abort, request
from app.user.models import User
from app.active_window.models import ActiveWindow
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist

active_window = Blueprint('active_window', __name__)

@active_window.route('/active-window/create/<email>', methods=['POST'])
def create_active_window(email):
    try:
        user = User.objects.get(email=email)
    except (MultipleObjectsReturned, DoesNotExist):
        abort(400)

    data_string = request.form.get('data')
    if not data_string:
        abort(400)

    data = json.loads(data_string)
    if not data:
        abort(400)

    for active_window_resource in data:
        time = active_window_resource.get('time')
        title = active_window_resource.get('title')
        if not time or not title:
            abort(400)

        aw = ActiveWindow(time=time, title=title, user=user)
        aw.save()
        user.active_windows.append(aw)

    user.save()
    return "Success!"