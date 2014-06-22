from flask import Blueprint, render_template
from app.user.models import User
import requests
from app import cache


base = Blueprint('base', __name__)

GITHUB_API = "https://api.github.com/repos/danrschlosser/cloaked-hipster/commits?page=%s"
MAX_PAGES = 4
def get_num_commits():
    num = cache.get('num_commits')
    if num is None:
        num = sum((len(requests.get(GITHUB_API%i).json()) for i in range(1, MAX_PAGES)))
        cache.set('num_commits', num, timeout=5*60)
        print "caclulated"
    return num




@base.route('/')
def index():
    commits = get_num_commits()
    users = User.objects()
    return render_template("home.html", users=users, commits=commits)
