#!/usr/bin/python
import os
import os.path as osp
import logging
import sys
from deployv.helpers.utils import parse_repo_url
from branchesv.branches import load as load_branches

_logger = logging.getLogger('CloneOCADeps')

TRAVIS_REPO_SLUG = os.environ.get("TRAVIS_REPO_SLUG")
TRAVIS_REPO_OWNER = TRAVIS_REPO_SLUG and TRAVIS_REPO_SLUG.split("/")[0]


def parse_depfile(depfile, version, owner='vauxoo'):
    """ This method, parse plain text file oca_dependencies.txt,
    if you have valid repository name, url and version
    :param depfile: object type open file
    :return: Returns list of tuples [(repo, url, version)]
    """
    deps = []
    for line in depfile:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        parts_count = len(parts)
        repo = parts[0]
        url = parts_count > 1 and parts[1]
        branch = parts_count > 2 and parts[2]
        commit = parts_count > 3 and parts[3]
        if not branch:
            branch = version
        if not url:
            url = 'https://github.com/%s/%s.git' % (owner, repo)
        if commit == '#':
            # It's not a commit, it's an inline comment
            commit = False
        deps.append((repo, url, branch, commit))
    return deps


def git_checkout(deps_checkout_dir, reponame, url, branch, commit=False,
                 tmp_folder=False, key_path=False):
    """ This method downloads the repositories found in the oca_dependencies
    files and clones them in the specified dir. If he specified directory
    where the dependencies will be cloned already exists
    and is not empty it won't clone the repos
    :param deps_checkout_dir: he directory in which the dependency
    repositories will be cloned
    :param reponame: name for repository
    :param url: url address repository
    :param branch: branch or version repository
    :param commit: Optional commit to clone
    :return: Returns list (full path)
    """
    repo = {
        'branch': branch, 'commit': commit, 'depth': 1, 'name': reponame,
        'path': reponame, 'repo_url': {'origin': url}
    }
    res = load_branches([repo], deps_checkout_dir, tmp_folder, key_path)
    if res:
        return (False, res.get('msg'))
    checkout_dir = osp.join(deps_checkout_dir, reponame)
    return (True, checkout_dir)


def get_dep_filename(deps_checkout_dir, build_dir, file_name,
                     version, tmp_folder, key_path=False):
    """ This method, makes a recursive search directories to get all the
    files listed in the parameters file_name (oca_dependencies.txt)
    :param deps_checkout_dir: he directory in which the dependency
    repositories will be cloned
    :param build_dir: the directory in which the tested
     repositories have been cloned
    :param file_name: filename to be searched
    :return: Returns list with absolute paths
    """
    dependencies = []
    processed = set()
    depfilename = osp.join(build_dir, file_name)
    dependencies.append((depfilename, 'vauxoo'))
    for repo in os.listdir(deps_checkout_dir):
        _logger.debug('examining %s', repo)
        processed.add(repo)
        depfilename = osp.join(deps_checkout_dir, repo, file_name)
        dependencies.append((depfilename, 'vauxoo'))
    for dependency in dependencies:
        try:
            owner = TRAVIS_REPO_OWNER or dependency[1]
            with open(dependency[0]) as depfile:
                deps = parse_depfile(depfile, version, owner=owner)
        except IOError:
            deps = []
        for depname, url, branch, commit in deps:
            _logger.debug('* processing %s', depname)
            if depname in processed:
                continue
            processed.add(depname)
            checkout_dir = git_checkout(
                deps_checkout_dir, depname, url, branch, commit, tmp_folder, key_path)
            if not checkout_dir[0]:
                return checkout_dir
            new_dep = (osp.join(checkout_dir[1], file_name),
                       get_owner_from_url(url))
            if new_dep not in dependencies:
                dependencies.append(new_dep)
    # Return the list of dependencies without the organization so we don't
    # have to modify the methods that receive this result
    res = [dep[0] for dep in dependencies]
    return (True, res)


def get_owner_from_url(url):
    """Parses the specified url in order to get the organization from it.
    This organization will be used to clone all the dependencies of this repo
    that does not have a specific url in the oca_dependencies.txt file. If the
    specified url is not in a correct format, this will return `vauxoo` by
    default.

    :param url: URL of the repo, can be http or ssh
    :type url: str
    :return: The organization of the specified repo (default: vauxoo)
    """
    url_parts = parse_repo_url(url)
    return url_parts.get('namespace') or 'vauxoo'


def run(deps_checkout_dir, build_dir, version, temp_folder, key_path=False):
    """ This method executes above methods
    :param deps_checkout_dir: he directory in which the dependency
    repositories will be cloned
    :param build_dir: the directory in which the tested
    repositories have been cloned
    """
    depens = get_dep_filename(deps_checkout_dir, build_dir, 'oca_dependencies.txt',
                              version, temp_folder, key_path)
    return depens


if __name__ == '__main__':
    run(*sys.argv[1:6])
