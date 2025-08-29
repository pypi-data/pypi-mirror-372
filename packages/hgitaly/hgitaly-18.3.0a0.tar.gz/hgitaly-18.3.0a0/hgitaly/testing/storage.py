from pathlib import Path

DEFAULT_STORAGE_NAME = 'default'
GIT_REPOS_STOWED_AWAY_PATH = Path('+hgitaly/hg-git')


def storage_path(server_repos_root, storage_name='default'):
    return server_repos_root / storage_name


def git_repo_path(server_repos_root, relpath, **kw):
    """Traditional path, as used before heptapod#1848."""
    relpath = Path(relpath).with_suffix('.git')
    return storage_path(server_repos_root, **kw) / relpath


def stowed_away_git_repo_relpath(relpath):
    """Stowed away relative path, as used for mirroring after heptapod#1848."""
    return (GIT_REPOS_STOWED_AWAY_PATH / relpath).with_suffix('.git')


def stowed_away_git_repo_path(server_repos_root, relpath,
                              **kw):
    """Stowed away path, as used for mirroring after heptapod#1848."""
    return git_repo_path(server_repos_root,
                         stowed_away_git_repo_relpath(relpath),
                         **kw)
