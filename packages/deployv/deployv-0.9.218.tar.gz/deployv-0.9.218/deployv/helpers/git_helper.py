# coding: utf-8

"""This module substitutes some functions from Gitlab or Github API"""
from os import path
from .utils import parse_repo_url, deploy_key, makedir, get_error_message, clean_files
from branchesv.branches import load as load_branches
from git import Git, exc as exceptions
import logging

_logger = logging.getLogger(__name__)


class GitManager:

    def __init__(self, temp_folder, repos_path=False, key_file=False):
        self.repos_path = repos_path or temp_folder
        self.temp_folder = temp_folder
        self.key_file = key_file

    def get_commit_history(self, repo, ref):
        """ Gets the commit history between the repository in ref repository.
        """
        _logger.debug("Repository: %s", repo)
        _logger.debug("Ref repository: %s", ref)
        config = self._get_config(repo)
        commits = []
        try:
            makedir(config['folder'])
            key_path = deploy_key(self.key_file, self.temp_folder)
            copy_repo = repo.copy()
            copy_repo.update({'path': repo['branch'], 'commit': '', 'depth': False})
            res = load_branches([copy_repo], config['folder'], self.temp_folder, key_path)
            msg_error = res and res.get('msg') or ''
            if not msg_error:
                res, commits = self._get_commits_history(
                    config['checkout_dir'], repo, ref.get('commit', ''))
                msg_error, commits = ('', commits) if res else (commits, [])
        except Exception as error:
            clean_files(config['checkout_dir'])
            msg_error = get_error_message(error)
        history = self._parse_commits_data(commits, repo, ref, msg_error)
        _logger.debug(history)
        return history

    def _get_config(self, repo):
        """Given a working folder returns the .git folder of the repository.

        :param repo: The repository where get the config.
        :type: dict
        :param working_folder: The folder where store the repostiroy.
        :type: str

        :return: return the config needs to get the commit history.
        :rtype: dict
        """
        res = parse_repo_url(repo['repo_url']['origin'])
        folder = path.join(self.repos_path, res['domain'], res['namespace'], res['repo_name'])
        clone_path = path.join(folder, repo['branch'])
        res.update({'folder': folder, 'checkout_dir': clone_path})
        return res

    def _get_commits_history(self, checkout_dir, repo, old_commit):
        """ Gets the commits between old commit and new commit.
        """
        res = []
        new_commit = repo.get('commit')
        gt = Git(checkout_dir)
        try:
            results = gt.log('--pretty=format:"%H%x00%ad%x00%ae%x00%an%x00%s"', '--date=iso',
                             '%(old)s..%(new)s' % {'old': old_commit, 'new': new_commit})
            lines = results.split('\n') or []
        except exceptions.GitCommandError as error:
            msg_error = get_error_message(error)
            return (False, msg_error)
        for line in lines:
            if not line:
                continue
            fields = line.replace('"', '').split('\x00')
            res.append({'commit': fields[0], 'date': fields[1], 'email': fields[2],
                        'author': fields[3], 'message': fields[4]})
        return (True, res)

    def _parse_commits_data(self, commits, repo, ref, error):
        repo_url = repo.get('repo_url').get('origin')
        commit_from = ref.get('commit') and ref.get('commit')
        commit_to = repo.get('commit') and repo.get('commit')
        commits = sorted(commits, key=lambda commit: commit['date'])
        return {
            'from': commit_from, 'to': commit_to, 'path': repo.get('path'),
            'branch': repo.get('branch'), 'name': repo.get('name'),
            'repo_url': repo_url, 'commits': commits or [], 'error': error or False,
        }
