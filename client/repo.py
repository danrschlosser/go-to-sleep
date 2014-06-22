
import git
import tempfile
import shutil

class GitRepo(object):

    def __init__(self):
        self.path = tempfile.mkdtemp()
        print self.path
        git.Git(self.path).init()
        self.repo = git.Repo(self.path)
        self.repo.git.commit(m=" 'test'", allow_empty=True)

    def update(self):
        print self.repo.is_dirty() 
        print self.repo.untracked_files
        if self.repo.is_dirty() or self.repo.untracked_files:
            self.repo.git.add('.')
            self.repo.git.commit(m=" test")
        stats = self.repo.head.commit.stats.total
        stats['files'] = self.repo.head.commit.stats.files.keys()
        del stats['lines']
        return stats

    def __del__(self):
        shutil.rmtree(self.path)

