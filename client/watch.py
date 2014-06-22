import sys
import time
import subprocess
import datetime
import requests
import json
from git import Repo
from window import current_window
from repo import GitRepo as gr
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class GitHandler(PatternMatchingEventHandler):
    patterns = ['*']

    # ROOT_URL = 'http://cloakedhipster.dyn.aeturnalus.com:5000/'
    ROOT_URL = 'http://localhost:5000/'

    @classmethod
    def sync_dir(cls, src, dest):
        def exclude(s):
            return '--exclude={}'.format(s)

        args = [
            'rsync',
            '-azr',
            '--delete',
            exclude('.git'),
            src,
            dest
        ]

        print args

        for exc in excludes:
            args.append(exclude(exc))

        print 'syncing {} to {}'.format(src, dest),

        try:
            subprocess.check_output(args)
        except subprocess.CalledProcessError as er:
            print 'errorcode: {}'.format(er.returncode)
            print 'output:'
            print er.output

    def __init__(self, path, excludes):
        super(GitHandler, self).__init__()
        self.path = path
        self.repo = Repo(path)
        self.user_email = self.repo.config_reader().get_value('user', 'email')
        self.user_name = self.repo.config_reader().get_value('user', 'name')
        self.latest_hash = self.repo.head.commit.hexsha
        self.excludes = excludes
        self.window_history = []

        self.gr = gr()

        self.tmp_root = self.gr.path
        self.is_dirty = False

        self.sync_dir(self.path, self.tmp_root)
        self.gr.update()

        self.create_user()

    def create_user(self):
        try:
            req = requests.post(self.ROOT_URL + 'users/create', data={
                'name': self.user_name,
                'email': self.user_email
            })
            print req.status_code
        except requests.ConnectionError as e:
            print '{} Could not creat user :('.format(e.errno)

    def format_upload(self, update):
        to_upload = {
            'lines_deleted': update.get('deletions'),
            'lines_inserted': update.get('insertions'),
            'files_changed': json.dumps(update.get('files')),
            'time': long(datetime.datetime.now().strftime('%s')),
            'base_hash': self.latest_hash,
            'remotes': json.dumps([r.url for r in self.repo.remotes])
        }
        return to_upload

    def upload_diff(self, diff):
        try:
            url = self.ROOT_URL + 'diff/' + self.user_email
            req = requests.post(url, data=diff)
            print req.status_code
        except requests.ConnectionError as e:
            print '{} NOOO ); it didn\'t work'.format(e.errno)

    def check_window(self):
        app, title = current_window()
        self.window_history.append({
            'app': app,
            'window_title': title,
            'time': long(datetime.datetime.now().strftime('%s')),
        })

    def send_window_dump(self):
        data = {'data': self.window_history}
        self.window_history = []    # reset window history
        try:
            url = self.ROOT_URL + 'active-window/create/' + self.user_email
            req = requests.post(url, data=data)
            print req.status_code
        except requests.ConnectionError as e:
            print '{} NOOO ); it didn\'t work for the window dump'.format(e.errno)

    def periodic_sync(self):
        print 'checking diff',
        self.latest_hash = self.repo.head.commit.hexsha
        if self.is_dirty:
            self.sync_dir(self.path, self.tmp_root)
            self.is_dirty = False
        update = self.gr.update()
        diff = self.format_upload(update)
        self.upload_diff(diff)
        self.send_window_dump()

    def process(self, event):
        self.is_dirty = True

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)

if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    path = args[0] if args else '.'

    excludes = []

    if len(args) > 1:
        is_exclude = False

        for a in args:
            if is_exclude:
                excludes.append(a)
                is_exclude = False
            elif a.startswith('-e'):
                is_exclude = True

    gh = GitHandler(path, excludes)

    observer.schedule(gh, path=path, recursive=True)
    observer.start()

    try:
        last_time = datetime.datetime.now()
        while True:
            now = datetime.datetime.now()
            gh.window_history()
            if now > last_time + datetime.timedelta(seconds=5):
                gh.periodic_sync()
                last_time = now
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
