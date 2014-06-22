
import git
import tempfile
import shutil

class GitRepo(object):

    def __init__(self):
        self.path = tempfile.mkdtemp()
        git.Git(self.path).init()
        self.repo = git.Repo(self.path)
        self.repo.git.commit(m=" 'test'", allow_empty=True)

    def update(self):
        print self.repo.git.status(untracked_files=True)
        print self.repo.untracked_files
        if self.repo.is_dirty(untracked_files=True):
            self.repo.git.add('.')
            self.repo.git.commit(m=" test")
        stats = self.repo.head.commit.stats.total
        stats['files'] = self.repo.head.commit.stats.files.keys()
        del stats['lines']
        return stats

    def __del__(self):
        shutil.rmtree(self.path)

