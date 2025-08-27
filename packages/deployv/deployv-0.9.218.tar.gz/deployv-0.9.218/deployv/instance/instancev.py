# coding: utf-8
""" As this class is a :class:`~base.DockerV` extension need to have the same values in the config
dictionary, but inside a config_container key::

        "container_config": {
            "apt_install": [],
            "pip_install": [],
            "domain": "localhost",
            "command": "sleep 20",
            "env_vars": {
                "odoo_config_file": "/home/odoo/.openerp_serverrc",
                "odoo_home": "/home/odoo",
                "odoo_user": "odoo"
            },
            "image_name": "busybox",
            "mem_limit": "768m",
            "ports": {
                "8069": 8069,
                "8072": None
            },
            "remove_previous": True,
            "working_folder": "/path/to/docker_volumes",
            "volumes":{
                "filestore": "/home/odoo/.local/share/Odoo",
                "logs": "/var/log/supervisor",
                "ssh": "/home/odoo/.ssh",
                "tmp": "/tmp"
            }
        },
        "instance": {
            "action_type": "replace",
            "task_id":"t1234",
            "customer_id": "customer80",
            "config": {
                "admin": "admin_pass",
                "admin_passwd": "123",
                "db_host": "172.17.42.1",
                "db_name": "{{ instance.task_id }}_{{ instance.customer_id }}",
                "db_password": "psql_user",
                "db_user": "psql_pass",
                "dbfilter": "{{ instance.task_id }}_{{ instance.customer_id }}.*",
                "list_db": True
            },
            "ssh_key":"base64_encoded_key",
            "repositories": [
                {
                    "branch": "8.0",
                    "commit": "8f159f276e7c8da4e5475e604e9057dcaadfedf9",
                    "depth": 1,
                    "is_dirty": False,
                    "name": "odoo",
                    "path": "odoo",
                    "repo_url": {
                        "origin": "git@github.com:Vauxoo/odoo.git"
                    },
                    "type": "git"
                },
            ],
            "update_module":"all",
            "install_module": None
        }

.. note:: For more information about *container_config* keys and values check
    :class:`~deployv.base.dockerv.DockerV` documentation

Where:

* *action_type*: Replace/create Odoo container
* *task_id*: associated task/issue/user story in the instance un the format [tiu]id
* *customer_id*: Unique customer id
* *config*: Dict with the values to be changed inside Odoo configuration file
* *ssh_key*: the id_rsa key ot be used to clone private repos, must be in base64 format
* *repositories*: A list of repos to be updated/added.
  Check `backupws <https://github.com/ruiztulio/backupws/blob/master/branches.py>`_
  if you want more detail about the format

"""
import tarfile
import logging
import github
from os import path, mkdir
from uuid import uuid4
import shutil
import time
import psycopg2
from psycopg2 import sql as psycopg2_sql
from docker.errors import APIError, ContainerError
import simplejson as json
import deployv_static
from passlib.context import CryptContext
from deployv.base.dockerv import DockerV
from deployv.base.postgresv import PostgresShell, PostgresConnector
from deployv.base import errors
from deployv.helpers import utils, container, database_helper, json_helper, pg_anon
from deployv.instance import ODOO_BINARY, PSQL_VERSIONS, TRAVIS_VERSIONS
from datetime import datetime
from jinja2 import Template


logger = logging.getLogger(__name__)  # pylint: disable=C0103
INSTANCE_TYPES = ['test', 'develop', 'updates', 'production']
ODOO_STAGES = {"production": "production", "updates": "staging",
               "develop": "dev", "test": "staging"}
UPDATE = ['develop', 'updates']
DEACTIVATE = ['test', 'develop', 'updates']
INSTALL_RIBBON = ['test', 'develop', 'updates']


class InstanceV(DockerV):

    def __init__(self, config, timeout=300, docker_url="unix://var/run/docker.sock"):
        self.__full_config = config
        self._skip_install_test_ribbon = False
        container_config = config.container_config
        logger.debug('Container config : %s',
                     json.dumps(container_config, sort_keys=True, indent=2))
        pg_container = '{prefix}_postgres'.format(prefix=config.prefix)
        container_config.update({'postgres_container_name': pg_container})
        if not container_config.get('container_name', False):
            container_config.update({
                'container_name': '{prefix}_odoo'.format(prefix=config.prefix)})
            env_vars = config.instance_config.get('config').copy()
            if not env_vars.get('admin'):
                env_vars.update({'admin': utils.random_string(6)})
            if not env_vars.get('admin_passwd'):
                env_vars.update({'admin_passwd': utils.random_string(6)})
            instance_type = config.instance_config.get('instance_type', 'production')
            env_vars.update({'instance_type': instance_type,
                             'odoo_stage': ODOO_STAGES.get(instance_type),
                             'customer': config.instance_config.get('customer_id')})
            self.__full_config.container_config.get('env_vars').update(env_vars)
        super(InstanceV, self).__init__(container_config,
                                        timeout=timeout, docker_url=docker_url)

    def start_odoo_container(self):
        """ Specifically starts an Odoo container and configure all the parameters,
        see :func:`~dockerv.DockerV.basic_info` for more information about the format and content

        :return: A dict with the basic info of container
        """
        # if it will be a full stack container all the parameters are changed (no matter what is
        # specified in the config) to target the local env and added the nginx, postgres and ssh
        # ports
        if self.config.get('full_stack', False):
            self.config.get('ports').update({'22': None})
        if (self.config.get('full_stack', False) or
                self.__full_config.backup_type in ['btrfs', 'zfs']):
            self.update_info_postgres_container()
        self.pull()
        logger.info('Starting Odoo container %s',
                    self.config.get('container_name'))
        self.config.update({'container_hostname': container.generate_hostname(self.__full_config)})
        info = self.deploy_container()
        time.sleep(10)
        if self.config.get('full_stack', False):
            self.add_authorized_keys()
            supervisor_status = self.check_supervisor()
            if not supervisor_status:
                return {'error': 'Supervisor process could not start'}
            postgres_connection = self.check_postgres()
            if not postgres_connection.get('success'):
                return postgres_connection
        self.set_global_env_vars()
        # Add the PGHOST and PGPORT env vars here because we only know which values to set after
        # the container is created, mainly because we don't know if the postgres is in
        # another container.
        self.exec_cmd(
            "/bin/bash -c 'echo export PGHOST={db_host} | tee -a /home/odoo/.profile'"
            .format(db_host=self.config.get('env_vars').get('db_host')))
        self.exec_cmd(
            "/bin/bash -c 'echo export PGPORT={db_port} | tee -a /home/odoo/.profile'"
            .format(db_port=self.config.get('env_vars').get('db_port')))
        logger.info('Odoo container "%s" created. Ports %s',
                    info.get('name'), info.get('ports'))
        return info

    def check_supervisor(self):
        retry = 0
        supervisor_process = self.exec_cmd('pgrep supervisord')
        if supervisor_process:
            return True
        while True:
            retry += 1
            chown_process = self.exec_cmd('pgrep chown')
            if chown_process:
                logger.debug('chown command is still running, retrying %s', retry)
                time.sleep(3)
                continue
            supervisor_process = self.exec_cmd('pgrep supervisord')
            if supervisor_process:
                return True
            return False

    def check_postgres(self):
        res = {'success': True}
        retry = 0
        config = self.db_config
        config.update({'db_name': 'template1'})
        while retry <= 3:
            logger.info('Testing postgres connection')
            try:
                conn = PostgresConnector(utils.odoo2postgres(config))
                conn.check_config()
                logger.info('Postgres connection test passed')
                return res
            except psycopg2.OperationalError as error:
                if 'the database system is starting up' in error.message:
                    retry += 1
                    logger.warning('Postgres is starting up, retry %s', retry)
                    time.sleep(5)
                    continue
                logger.error(
                    'Could not connect to the postgres server: %s',
                    error.message)
                res.update({'success': False, 'error': error.message})
                return res

    def add_authorized_keys(self):
        tmp = self.__full_config.temp_folder or '/tmp'
        git_cli = github.Github()
        users = self.__full_config.instance_config.get('authorized_users', [])
        authorized_keys_path = path.join(tmp, 'authorized_keys')
        authorized_keys_tar_path = path.join(tmp, 'keys.tar')
        with open(authorized_keys_path, 'w') as authorized_keys:
            for user in users:
                user_keys = []
                try:
                    user_keys = git_cli.get_user(user).get_keys()
                except github.GithubException as error:
                    error_msg = error.data.get('message')
                    if 'Not Found' in error_msg:
                        logger.warning('User not found %s, could not retrieve any key', user)
                    else:
                        logger.warning(error_msg)
                for user_key in user_keys:
                    authorized_keys.write(user_key.key + '\n')
        with tarfile.open(authorized_keys_tar_path, 'w') as tar_keys:
            tar_keys.add(authorized_keys_path, arcname='authorized_keys')
        with open(authorized_keys_tar_path, 'r') as tar_data:
            self.cli.put_archive(self.config.get('container_name'),
                                 '/home/odoo/.ssh/', tar_data.read())
            self.exec_cmd('chown odoo:odoo /home/odoo/.ssh/authorized_keys')
            self.exec_cmd('cp /home/odoo/.ssh/authorized_keys /root/.ssh/')
            self.exec_cmd('chown root:root /root/.ssh/authorized_keys')
        utils.clean_files([authorized_keys_tar_path, authorized_keys_path])

    @property
    def is_running(self):
        """ If the Odoo instance ins running inside the container (or at least supervisord
        detects it) return True, False otherwise. If an unexpected state is detected raises
        a SupervisorStatusError exception

        :return: True or False
        """
        retry_triggers = [
            'refused connection', 'no such file', 'STARTING', 'STOPPING', 'BACKOFF']
        retry = 0
        while retry <= 3:
            try:
                res = self.exec_cmd('supervisorctl status ' + self.supervisor_app)
            except errors.NotRunning:
                retry += 1
                logger.debug('Container not running, retry %s', retry)
                time.sleep(4)
                continue
            logger.debug('is_running: %s', res.strip())
            if 'RUNNING' in res:
                return True
            if 'STOPPED' in res:
                return False
            if retry < 3 and any([msg for msg in retry_triggers if msg in res or res == '']):
                retry += 1
                logger.debug('The Odoo process is in an intermediate state or'
                             ' is not running yet, retrying %s', retry)
                time.sleep(4)
            else:
                raise errors.SupervisorStatusError('Unknown state: %s' % res)

    @property
    def instance_type(self):
        """ The instance type

        :return: Instance type: production, test, develop or false if it not set
        """
        return self.__full_config.instance_config.get('instance_type') or\
            self.docker_env.get('instance_type', 'production')

    @property
    def temp_folder(self):
        """ This is a very important property because the tmp folder is used to share files between
            the container and the host, widely used along the code.
            The best way (so far) is iterating all the mounted volumes until we find the /tmp

        :return: Full host path where the tmp volume is mounted
        """
        res = None
        try:
            inspected = self.inspect()
        except errors.NoSuchContainer:
            return res
        volumes = inspected.get('Mounts')
        for volume in volumes:
            if volume.get("Destination") == '/tmp' and volume:
                res = volume.get("Source")
                break
        return res

    @property
    def odoo_binary(self):
        return ODOO_BINARY[self.config_variables.get('version')]

    @property
    def supervisor_group(self):
        ct = self.config_variables.get('container_type')
        if ct == 'MULTIODOO':
            return 'multiodoo:*'
        return 'odoo'

    @property
    def supervisor_app(self):
        ct = self.config_variables.get('container_type')
        if ct == 'MULTIODOO':
            return 'multiodoo:odoo'
        return 'odoo'

    def start_instance(self):
        """ Start an instance inside a docker container using supervisord

        :return: Supervisord response
        """
        res = 'RUNNING'
        if not self.is_running:
            res = self.exec_cmd('supervisorctl start ' + self.supervisor_group)
            logger.debug('start_instance: %s', res.strip())
        return res

    def stop_instance(self):
        """ Stop an instance inside a docker container using supervisord

        :return: Supervisord response
        """
        res = 'STOPPED'
        if self.is_running:
            res = self.exec_cmd('supervisorctl stop ' + self.supervisor_group)
            logger.info('stop_instance: %s', res.strip())
        return res

    def ensure_process_check(self, process, check, possible_exceptions=False, max_tries=False):
        """Runs a given process and ensures that the result is the one that you want. If it is
        not, the process will run as many times as specified in max_tries, or until the check
        is passed.

        :param process: The process you want to run until it checks out. Should be a lambda
            function that receives the instance as the only param and returns the result of the
            process to be validated.
        :type process: lambda
        :param check: The check method for the value returned from process. Should be a lambda
            function that receives the result of the process function as the only param, checks
            the value is the expected one, and returns a boolean with that result.
        :type check: lambda
        :param possible_exceptions: A set of possible exceptions (classes) that can be raised
            from the process.
        :type possible_exceptions: set
        :param max_tries: The amount of times the given process will run until the result of the
            process is the expected one.
        :type max_tries: int
        """
        ok = False
        tries = 0
        if not possible_exceptions:
            possible_exceptions = Exception
        while tries < (max_tries or 99) and not ok:
            tries += 1
            try:
                process_result = process(self)
            except possible_exceptions:  # pylint: disable=E0712,W0703
                ok = False
            else:
                ok = check(self, process_result)
            if not ok:
                time.sleep(3)
        return ok

    def ensure_instance_status(self, ensure_running, max_tries=False):
        """Starts/stops an instance and ensures is either running or not, checking as many
        times as specified in max_tries.

        :param ensure_running: If True, it will start and ensure that the instance is running.
            If False, it will stop and ensure that the instance is not running.
        :type ensure_running: bool
        :param max_tries: The amount of times it will check
        :type max_tries: int
        """
        supervisor = self.ensure_process_check(
            lambda ins: ins.exec_cmd('pgrep supervisord'),
            lambda ins, res: bool(res),
            False, max_tries)
        if not supervisor:
            return False
        command = self.ensure_process_check(
            lambda ins: (
                ins.start_instance() if ensure_running
                else ins.stop_instance()
            ),
            lambda ins, res: bool(res),
            errors.SupervisorStatusError, max_tries)
        if not command:
            return False
        status = self.ensure_process_check(
            lambda ins: ins.is_running,
            lambda ins, res: res is ensure_running,
            False, max_tries)
        return status

    def run_and_log(self, command, attachment_name=False, skip_summary=False):
        """ Executes an Odoo related command inside the container (i.e.: update, install) and
            returns the resumed log and full path to the generated log. See
            :func:`~dockerv.helpers.utils.resume_log` for detailed information about
            the return format

        :param command: Command line to be executed inside Odoo container
        :return: Resumed log and full path to the generated file
        """
        self.stop_instance()
        logger.debug('run_and_log: %s', command)
        res = self.exec_cmd(command)
        resume = utils.resume_log(res.split('\n'))
        self.start_instance()
        attachment_name = (
            attachment_name or 'cmd_{timestamp}.log'.format(timestamp=utils.get_strtime())
        )
        working_path = path.join(self.temp_folder, attachment_name)
        with open(working_path, 'w') as log_file:
            log_file.write(res)
        resume.update({'log_file': working_path})
        if not skip_summary:
            logger.info('+-- Critical errors %s', len(resume.get('critical')))
            logger.info('+-- Errors %s', len(resume.get('errors')))
            logger.info('+-- Import errors %s', len(resume.get('import_errors')))
            logger.info('+-- Warnings %s', len(resume.get('warnings')))
            logger.info('+-- Translation Warnings %s', len(resume.get('warnings_trans')))
        logger.info('Logger was saved to: "%s"', working_path)
        return resume

    def update_db(self, db_name, modules=False):
        """ Updates the database using one of the possible methods of updating.

        Possible methods:
            - cou: uses click-odoo-update to update the modules that changed in the db.
            - normal: updates the provided modules or the ones specified in the json.

        :param db_name: Database name to be updated
        :param modules: List of modules to update, only used by the normal method.
        :return: Resumed log and full path to the generated file
        """
        if not self.__full_config.update_method:
            self.__full_config.update_method = 'normal'
        update_methods = {
            'cou': self._cou_update,
            'normal': self._module_update
        }
        if self.__full_config.update_method not in update_methods:
            return {'error': 'Unknown update method: %s' % self.__full_config.update_method}
        update_method = update_methods[self.__full_config.update_method]
        res = update_method(db_name)
        return res

    def _module_update(self, db_name):
        """ Updates the specified database by executing -u module for each module in
        the json.

        :param db_name: Name of the database to update.
        :return: dict with the logs of the update and the summary of the results.
        """
        res = {'result': {'update_logs': []}, 'attachments': []}
        image_name = self.config.get('image_name') or self.basic_info.get('image_name')
        modules = self.__full_config.instance_config.get('update_module') or []
        logger.info('Updating database %s with the image %s, modules %s',
                    db_name, image_name, modules)
        working_folder = path.join(self.config.get("working_folder"),
                                   self.config.get('container_name'))
        data_dir = self.get_data_dir()
        working_folder = data_dir.replace('filestore', '') if data_dir else working_folder
        db_config = self.db_config
        for entrypoint in ['/entry_point', '/entrypoint', '/entry_point.py']:
            entrypoint_exists = self.exec_cmd_image(
                'test -x %s' % entrypoint, self.config.get('volumes'),
                working_folder, image=image_name)
            if not entrypoint_exists.get('error'):
                break
        odoo_conf_exists = self.exec_cmd_image(
            'test -f /home/odoo/.odoorc', self.config.get('volumes'),
            working_folder, image=image_name)
        odoo_conf_file = ('/home/odoo/.odoorc' if not odoo_conf_exists.get('error') else
                          '/home/odoo/.openerp_serverrc')
        update_command = (
            "{entrypoint} run --user odoo '/home/odoo/instance/odoo/{odoo}"
            " -c {odoo_conf}"
            " -d {database} -u {{module}} --logfile {{log}} --stop-after-init'"
            .format(entrypoint=entrypoint, odoo=self.odoo_binary, database=db_name,
                    odoo_conf=odoo_conf_file))
        pg_shell = PostgresShell(utils.odoo2postgres(db_config))
        for module in modules:
            for attempt in range(2):
                log_file = 'update_{mod}_{date}.log'.format(mod=module, date=utils.get_strtime())
                log_path = path.join('/tmp/deployvlogs/', log_file)
                local_path = path.expanduser(path.join(working_folder, log_path.strip('/')))
                command = update_command.format(module=module, log=log_path)
                logger.info('Updating "%s"', module)
                # Terminate connections before updating
                pg_shell.terminate_sessions(db_name, db_config.get('db_owner'),
                                            db_config.get('db_owner_passwd'))
                try:
                    self.exec_cmd_image(command, self.config.get('volumes'),
                                        working_folder, image_name)
                except (ContainerError, APIError) as error:
                    res.update({'error': 'Error updating "{mod}": {err}'.format(
                        mod=module, err=utils.get_error_message(error))})
                    parsed_log = self._parse_update_log(local_path, module)
                    summary = parsed_log.get('summary')
                    if summary:
                        res['result']['update_logs'].append(summary)
                        res['attachments'].append(parsed_log.get('attachment'))
                    return res
                logger.info('Log was saved to "%s"', local_path)
                parsed_log = self._parse_update_log(local_path, module)
                if parsed_log.get('error') and not parsed_log.get('summary'):
                    # Return the error message if the log file couldn't be generated
                    res.update(parsed_log)
                    return res
                summary = parsed_log.get('summary')
                if parsed_log.get('error'):
                    if attempt:
                        res.update({'error': parsed_log.get('error')})
                        res['result']['update_logs'].append(summary)
                        res['attachments'].append(parsed_log.get('attachment'))
                        return res
                    logger.info('An error occured, trying again')
                    continue
                res['result']['update_logs'].append(summary)
                res['attachments'].append(parsed_log.get('attachment'))
                break
        return res

    def _cou_update(self, db_name):
        """ Updates the specified database by executing the click-odoo-update script
        from the OCA, which automatically detects the modules that changed and updates them.

        :param db_name: Name of the database to update.
        :return: dict with the logs of the update and the summary of the results.
        """
        res = {'result': {'update_logs': []}, 'attachments': []}
        image_name = self.config.get('image_name') or self.basic_info.get('image_name')
        working_folder = path.join(self.config.get("working_folder"),
                                   self.config.get('container_name'))
        data_dir = self.get_data_dir()
        working_folder = data_dir.replace('filestore', '') if data_dir else working_folder
        logger.info('Updating database %s using COU', db_name)
        entrypoint_exists = self.exec_cmd_image(
            'test -x /entry_point', self.config.get('volumes'), working_folder, image=image_name)
        entrypoint = '/entry_point' if not entrypoint_exists.get('error') else '/entry_point.py'
        update_command = "{entrypoint} cou -d {database}".format(
            entrypoint=entrypoint, database=db_name)
        local_log_path = path.expanduser(
            path.join(working_folder, 'tmp/deployvlogs/cou_update.log'))
        pg_shell = PostgresShell(utils.odoo2postgres(self.db_config))
        for attempt in range(2):
            # Terminate connections before updating
            pg_shell.terminate_sessions(db_name, self.db_config.get('db_owner'),
                                        self.db_config.get('db_owner_passwd'))
            try:
                self.exec_cmd_image(update_command, self.config.get('volumes'),
                                    working_folder, image_name)
            except (ContainerError, APIError) as error:
                res.update({'error': 'Error updating using COU: {err}'.format(
                    err=utils.get_error_message(error))})
                parsed_log = self._parse_update_log(local_log_path, 'COU')
                summary = parsed_log.get('summary')
                if summary:
                    res['result']['update_logs'].append(summary)
                    res['attachments'].append(parsed_log.get('attachment'))
                return res
            logger.info('Log was saved to "%s"', local_log_path)
            parsed_log = self._parse_update_log(local_log_path, 'COU')
            if parsed_log.get('error') and not parsed_log.get('summary'):
                # Return the error message if the log file couldn't be generated
                res.update(parsed_log)
                return res
            summary = parsed_log.get('summary')
            if parsed_log.get('error'):
                if attempt:
                    res.update({'error': parsed_log.get('error')})
                    res['result']['update_logs'].append(summary)
                    res['attachments'].append(parsed_log.get('attachment'))
                    return res
                logger.info('An error occured, trying again')
                continue
            res['result']['update_logs'].append(summary)
            res['attachments'].append(parsed_log.get('attachment'))
            break
        return res

    def _parse_update_log(self, log_path, module):
        res = {}
        try:
            with open(log_path) as log_file:
                summary = utils.resume_log(log_file)
        except IOError as error:
            res.update({'error': 'Could not open log "{log}": {err}'.format(
                log=log_path, err=utils.get_error_message(error))
            })
            return res
        for log_type, log_num in sorted(summary.items(), key=lambda log: log[0]):
            logger.info('+-- %s %s', log_type.replace('_', ' ').title(), len(log_num))
        summary.update({'log_file': log_path})
        if summary.get('errors') or summary.get('critical'):
            update_error = 'An error ocurred while updating "{mod}"'.format(mod=module)
            res.update({'error': update_error})
            logger.error(update_error)
        res.update({
            'summary': summary,
            'attachment': {
                'file_name': path.basename(log_path),
                'file': utils.generate_attachment(log_path),
                'type': 'text/plain'
            }
        })
        return res

    def install_module(self, modules, db_name, without_demo=True):
        """ Executes "-i module" or "-i module1,module2" on the selected database and returns
            resumed log and full path to the generated log. See
            :func:`~dockerv.helpers.utils.resume_log` for detailed
            information about the return format

        :param modules: Module (str) o modules (list) to be installed
        :param db_name: Database name to be updated
        :param without_demo: Install the mdule/s with or without demo,
            if true will use --without-demo=all, if false omit the option,
            otherwise the module list
        :return: Resumed log and full path to the generated file
        """
        if utils.is_iterable(modules):
            modules_str = ','.join(modules)
        else:
            modules_str = modules

        if isinstance(without_demo, bool):
            wodemo = '--without-demo=all' if without_demo else ''
        elif utils.is_iterable(modules):
            wodemo = '--without-demo={}'.format(','.join(modules))
        elif isinstance(without_demo, str):
            wodemo = '--without-demo={}'.format(modules)
        logger.info('Installing modules %s in database %s',
                    modules_str, db_name)
        command_odoo = self.odoo_binary
        if self.config.get('env_vars'):
            env_vars = self.config.get('env_vars')
            if env_vars.get('odoo_home') and env_vars.get('odoo_user'):
                odoo_home = env_vars.get('odoo_home')
                odoo_user = env_vars.get('odoo_user')
        else:
            odoo_home = self.docker_env.get('odoo_home')
            odoo_user = self.docker_env.get('odoo_user')

        update_command = ('su {user} -c "{home}/instance/odoo/{odoo}'
                          ' -d {database} -i {modules} --stop-after-init {wodemo}"') \
            .format(home=odoo_home, user=odoo_user, database=db_name, modules=modules_str,
                    wodemo=wodemo, odoo=command_odoo)
        skip_modules = ['web_environment_ribbon_isolated']
        skip_summary = all(module in skip_modules for module in modules_str.split(','))
        attachment_name = 'install_{mod}_{timestamp}.log'.format(
            timestamp=utils.get_strtime(), mod=modules_str)
        return self.run_and_log(update_command, attachment_name, skip_summary)

    def move_file(self, filename):
        """Moves a file into the container temp shared volume

        :filename: File to be moved
        """
        actual_path = path.dirname(path.realpath(__file__))
        file_lib_src = path.join(
            actual_path, '..', 'helpers', filename)
        file_lib_dst = path.join(self.temp_folder, filename)
        shutil.copyfile(file_lib_src, file_lib_dst)

    def start_postgres_container(self):
        """ Specifically starts an Postgres container and configure users and connections,
        see :func:`~dockerv.DockerV.basic_info` for more information about the format and content

        :return: A dict with the basic info of container
        """
        if (not self.__full_config.container_config.get('postgres_container') or
                self.__full_config.backup_type in ['btrfs', 'zfs']):
            return {}
        destination = '/var/log/pg_log'
        res = self.update_info_postgres_container()
        if res:
            return {}
        ins_config = self.config.copy()
        psql_version = self.get_postgres_version()
        psql_image = self.__full_config.psql_image or \
            "postgres:{version}".format(version=psql_version)
        role = 'createdb'
        self.config.get('volumes').update({'postgresql/data': '/var/lib/postgresql/data/pgdata'})
        if self.config.get('full_stack'):
            role = 'superuser'
            self.config.get('volumes').update({'pg_log': destination})
        self.config.update({"image_name": psql_image})
        self.pull()
        self.config.update({'ports': {'5432': self.db_config.get('db_export_port') or None}})
        self.config.get('env_vars').update({
            'db_host': '127.0.0.1',
            'db_port': 5432,
            'postgres_password': 'postgres',
            'pgdata': '/var/lib/postgresql/data/pgdata',
            'pg_log_path': destination
        })
        self.config.update({"container_name": self.config.get('postgres_container_name')})
        self.config.update({'container_hostname': container.generate_hostname(self.__full_config)})
        self.config.update({'command': ''})
        res = self.deploy_container()
        while 'accepting connections' not in self.exec_cmd('pg_isready', user='postgres'):
            time.sleep(3)
        cmd = "psql -c \"create user {user} with password '{password}' {role}\"".\
            format(user=self.db_config.get('db_user'), role=role,
                   password=self.db_config.get('db_password'))
        self.exec_cmd(cmd, user="postgres")
        # Create onwer user in postgreSQL
        cmd = "psql -c \"create user {user} with password '{password}' superuser\"".\
            format(user=self.db_config.get('db_owner'),
                   password=self.db_config.get('db_owner_passwd'))
        self.exec_cmd(cmd, user="postgres")
        info = self.inspect()
        self.config.update(ins_config)
        self.config.get('volumes').pop('pg_log', False)
        self.config.update({
            'pg_log_postgres': self.get_specify_volumen(info, destination)})
        db_host = info.get('NetworkSettings').get('Gateway')
        db_port = self.get_db_port(info)
        self.config.get('env_vars').update({
            'db_host': db_host, 'external_db_port': db_port, 'db_port': db_port})
        self.__full_config.instance_config.get('config').update({
            'db_host': db_host, 'db_port': db_port})
        # Don't expose the 5432 port in the odoo container
        # if a postgres container was created
        self.config.get('ports').pop('5432', False)
        self.unset_docker_id()
        return res

    def get_postgres_version(self):
        """Helper method used to obtain the postgres version required for this version of odoo.
        This makes it easier to get the information used for the btrfs/zfs requests and the
        information required to create the postgres containers.
        """
        try:
            image_data = self.inspect_image(self.config.get('image_name'))
            vars_list = image_data.get('Config').get('Env')
        except errors.NoSuchImage:
            vars_list = []
        image_vars = container.parse_env_vars(vars_list)
        psql_version = image_vars.get('psql_version', '9.6')
        return psql_version

    def get_specify_volumen(self, info, volume_path):
        """Get a specify volumen from the information of container.
        """
        source = [volume.get('Source') for volume in info.get('Mounts')
                  if volume.get('Destination') == volume_path]
        return source and source[0] or False

    def get_db_port(self, info_inspected):
        """Get the database port that use in the postgres container
        the instance to connect with postgres.

        :param info_inspected: The information of container.
        :type info_inspected: dict

        :return: the port that use the instance to connect with postgres.
        """
        ports = container.get_ports_dict(info_inspected)
        db_port = ports.get('5432')
        if isinstance(db_port, list):
            db_port = db_port[0].split(':')[1]
        return db_port

    def restore_database(self, db_name=False, backup_dir=False):
        res = {'result': {}}
        error = False
        db_name_config = self.__full_config.instance_config.get('config').get('db_name')
        customer_id = (self.__full_config.instance_config.get('customer_id') or
                       self.docker_env and self.docker_env.get("customer"))
        if not customer_id:
            error = 'No such customer to restore the database'
        if error:
            return {'error': error}
        logger.debug('Psql in container: %s', self.config.get('postgres_container', False))
        self.start_postgres_container()
        use_template = self.__full_config.container_config.get('use_template')
        jobs = self.__full_config.jobs or 5
        helper_obj = database_helper.DatabaseHelper.get_helper(use_template)
        extensions = self.__full_config.postgres.get('extensions')
        if (self.__full_config.instance_config.get('customer_id')
                in self.__full_config.postgres.get('avoid_postgis', [])):
            try:
                extensions.remove('postgis')
            except ValueError:
                pass
            try:
                extensions.remove('postgis_topology')
            except ValueError:
                pass
        db_helper = helper_obj(
            utils.odoo2postgres(self.db_config), self._get_admin_config(),
            extensions)
        backup_dir = backup_dir or self.__full_config.backup_src
        res_search = db_helper.search_candidate(backup_dir, customer_id)
        if not res_search[0]:
            return {'error': res_search[1]}
        res.get('result').update({'backup': path.basename(res_search[1])})
        try:
            candidate = utils.decompress_files(
                res_search[1], self.__full_config.temp_working_folder)
        except (EOFError, IOError) as error:
            res.update({'error': utils.get_error_message(error)})
            return res
        backup_size = utils.get_size(candidate)
        res.get('result').update({'backup': path.basename(candidate),
                                  'source': candidate, 'backup_size': backup_size})
        filestore = path.join(candidate, 'filestore')
        db_name = db_name or db_name_config or utils.generate_dbname(
            self.__full_config, path.basename(res_search[1]), self.__full_config.prefix)
        if self.docker_id:
            self.stop_instance()
        logger.info("Start restore database")
        create_res = db_helper.create_database(candidate, db_name, self.db_config.get('db_owner'),
                                               self.db_config.get('db_owner_passwd'), jobs=jobs)
        if not create_res[0]:
            res.update({'error': create_res[1]})
            return res
        logger.info("Database restored")
        create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.docker_id and path.exists(filestore):
            filestore_res = self.restore_filestore(filestore, db_name)
            if filestore_res.get('error'):
                return filestore_res
        else:
            self.__full_config.instance_config.update({
                'restore_filestore': {'path': filestore, 'db_name': db_name}})
        res.get('result').update({'database_name': db_name, 'create_date': create_date})
        self.create_extension_unaccent(db_name)
        return res

    def files2backup(self, database_name, tmp_dir, data_dir=False):
        """ Generates the files that will be added to the backup, such as
        json with the information of the repositories used in that instance,
        filestore and db dump.

        :param database_name: Name of the database that will be dumped
        :param tmp_dir: Temporal directory where the dump will be stored
        :returns: List of the files that will be compressed in the backup
        """
        files = []
        jobs = self.__full_config.jobs
        postgres_cfg = self.db_config
        data_dir = data_dir or postgres_cfg.get('data_dir')
        postgres_cfg.update({'database': database_name})
        postgres = PostgresShell(utils.odoo2postgres(postgres_cfg))
        dump_base_name = 'dump.sql' if not jobs else 'database_dump'
        dump_name = path.join(tmp_dir, dump_base_name)
        exclude = self.__full_config.postgres.get("exclude_tables") or ""
        dump_name = postgres.dump(database_name, dump_name, jobs=jobs, exclude=exclude)
        if not dump_name:
            logger.error('Database could not be dumped')
            return files
        files.append(
            dump_name if not path.isdir(dump_name) else (dump_name, path.basename(dump_name))
        )
        try:
            manifest_path = self._get_db_manifest(tmp_dir)
            files.append(manifest_path)
        except errors.CommandError as error:
            error_msg = utils.get_error_message(error)
            # TODO: Only log an error when the container does not exist to provide
            # the same treatment as the filestore, this allows us to generate a
            # backup with the required files during the production release, where
            # the container doesn't exist but the files are obtained from another
            # place. We need to improve this logic in the future though.
            if 'Container does not exist' not in error_msg:
                raise
            logger.error('The container %s does not exist,'
                         ' manifest file won\'t be added to the backup',
                         self.docker_id or self.config.get('container_name'))
        if data_dir:
            attachments_folder = path.join(
                data_dir, 'filestore', postgres_cfg.get('database')
            )
            if path.exists(attachments_folder):
                logger.debug('Attachments folder "%s"', attachments_folder)
                files.append((attachments_folder, 'filestore'))
            else:
                logger.warning(
                    'Folder "%s" does not exists, attachments are not being '
                    'added to the backup', attachments_folder)
        else:
            logger.info('There is not attachments folder to backup')
        try:
            json_repos = self.save_repositories("repositories.json")
            if path.exists(json_repos):
                files.append((json_repos, 'repositories.json'))
        except errors.CommandError as error:
            error_msg = utils.get_error_message(error)
            logger.warning('Failed to generate the branches json: \n%s', error_msg)
        return files

    def compress_files(self, files, backup_name, destination, cformat):
        """ Creates a compressed file in the specified destination with the name,
        format, and files provided.

        :param files: List of  files that will be added to the compressed file
        :param backup_name: Name of the compressed file that will be created
        :param destination: Directory where the compressed file will be created
        :param cformat: Format used to compress the files (bz2, gz)
        :return: Name of the new compressed file
        """
        logger.info('Compressing files')
        logger.debug('Files : %s', str(files))
        full_name = utils.compress_files(
            backup_name, files, dest_folder=destination, cformat=cformat)
        logger.info('Compressed backup, cleaning')
        for element in files:
            if not hasattr(element, '__iter__'):
                utils.clean_files(element)
        return full_name

    def generate_backup(self, params):
        """ Generate an instance backup that contains:
            - Database dump in sql format
            - A folder with instance attachments called *filestore*
            - Json file with the repos ans hashes from the actual instance

        .. note:: If the method cannot access the filestore folder it won't be included in the
            backup

        :param dest_folder: Folder where the backup will be stored
        :param  reason: Optional parameter that is used in case
                          there is a particular reason for the backup
        :return: Full path to the generated backup
        """
        additional_files = params.get('additional_files') or []
        reason = params.get('reason') or self.__full_config.reason
        prefix = params.get('prefix') or self.__full_config.prefix
        cformat = params.get('cformat') or self.__full_config.cformat
        db_name = params.get('db_name')
        try:
            files = self.files2backup(
                db_name, self.__full_config.temp_working_folder, params.get('data_dir'))
        except errors.DumpError as error:
            logger.error('An error raise during the database backup, cleaning up')
            raise error  # pylint: disable=E0702
        files.extend(additional_files)
        bkp_name = utils.generate_backup_name(db_name, reason, prefix)
        res = self.return_backup(files, bkp_name, params.get('dest_folder'), cformat)
        return res

    def return_backup(self, files, bkp_name, dest_folder, cformat):
        if not cformat:
            return {'files': files, 'name': bkp_name,
                    'tmp_dir': self.__full_config.temp_working_folder}
        if cformat == 'folder':
            res = self._generate_decompressed_backup(
                files, bkp_name, dest_folder
            )
        else:
            res = self.compress_files(files, bkp_name, dest_folder, cformat)
        return res

    def _generate_decompressed_backup(self, files, name, destination):
        """Moves all the files obtained during the backup to a folder
        with the specified name in the destionation.

        :param files: list of paths to the files that will be added to the backup
        :param name: name of the new backup
        :param destination: directory where the new backup will be store
        """
        logger.info('Generating decompressed backup')
        tmp_name = path.join(destination, '._{}'.format(name))
        logger.info('Creating temp folder %s', tmp_name)
        mkdir(tmp_name)
        logger.info('Temp folder created')
        for file_path in files:
            is_iterable = utils.is_iterable(file_path)
            src = file_path if not is_iterable else file_path[0]
            dest = (path.join(tmp_name, path.basename(file_path)) if not is_iterable else
                    path.join(tmp_name, file_path[1]))
            logger.info('Adding file %s to %s', src, dest)
            if path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy(src, dest)
        res = path.join(destination, name)
        shutil.move(tmp_name, res)
        logger.info('Backup %s generated', res)
        return res

    def restore_filestore(self, src_folder, database_name):
        """ Restore a filestore folder into a docker container that is already running
            and has the /tmp folder mounted as a volume un the host

        :param src_folder: Full path to the folder that contains the filestore you want to restore
        :param database_name: Database name being restored
        """
        logger.info("Restoring filestore")
        working_folder = path.join(self.config.get("working_folder"),
                                   self.config.get('container_name'))
        dest = path.join(path.expanduser(working_folder), 'filestore')
        dest = self.get_data_dir() or dest
        volumes = {
            path.abspath(src_folder): {
                'bind': '/tmp/filestore',
                'ro': False,
            },
            dest: {
                'bind': self.config.get('volumes').get('filestore'),
                'ro': False
            }
        }
        cmd_filestore = ("(ls {fsname} 2>/dev/null && cp -R /tmp/filestore/* {fsname}) "
                         "|| cp -R /tmp/filestore {fsname}")
        if self.__full_config.deployer.get('use_rsync'):
            cmd_filestore = ("apt update && apt-get install rsync && "
                             "rsync -rza /tmp/filestore/ {fsname}/")
        bash_lines = [
            # Add "/*" to the end of path because it trigger an error when it's mount in ZFS path
            # and tries to restore a manual backup.
            "rm -rf {fsname}/*",
            "mkdir -p /home/odoo/.local/share/Odoo/filestore/",
            # TODO: Remove the install of `rsync` when all the customers image have installed
            # the package, because it doesn't installed it will trigger an error.
            cmd_filestore,
            "chown -R odoo:odoo /home/odoo/.local",
            "chmod -R o+r {fsname}"
        ]
        res = self.execute_in_auxiliary_container(database_name, bash_lines, volumes)
        logger.info("Filestore restored")
        return res

    def execute_in_auxiliary_container(self, db_name, commands, volumes=False):
        """Method that creates an auxiliary container copy of the
        instance and executes the provided commands in a single docker
        run (the commands are separated by `&&`). This is so we can execute
        commands that modify data contained in the container's volumes that
        may require too many resources without taking the risk of killing
        the main container.

        :param db_name: Name of the database, use to know where the volumes
            created by deployv are.
        :type db_name: str
        :param commands: List of commands to be executed
        :type commands: list
        :return: Dictionary with the `result` key (list) if all the commands are
            executed, and/or the `error` key (list) if any or all of them failed.
        """
        res = {}
        results = []
        errors_list = []
        logger.debug('Getting properties')
        fs_name = path.join('/home/odoo/.local/share/Odoo/filestore/', db_name)
        logger.debug('Creating auxiliary container')
        for cmd in commands:
            cmd = cmd.format(fsname=fs_name)
            try:
                container_cfg = self.inspect()
            except errors.NoSuchContainer:
                container_cfg = {}
            image = container_cfg.get('Config', {}).get('Image') or self.config.get('image_name')
            cmd_res = self.exec_cmd_image("bash -c '%s'" % (cmd), volumes, image=image)
            if cmd_res.get('error'):
                errors_list.append(cmd_res['error'])
            elif cmd_res.get('result'):
                results.append(cmd_res['result'])
        if results:
            res.update({'result': '\n'.join(results)})
        if errors_list:
            res.update({'error': '\n'.join(errors_list)})
        return res

    def execute_query(self, db_config, query, allow_errors=False, with_as_write=False):
        """Executes the provided query upon the specified database.

        :param db_config: Name of the database where the query will be executed,
        :param query: SQL query to execute.
        :param allow_errors: If True, the errors raised regarding missing or already
            existing tables while executing the query will be ignored, a
            psycopg2.ProgrammingError will be raised otherwise.
        :param with_as_write: indicates if with sentence should be interpreted
            as a changing sentence (like insert, update), and return True when executed
            instead of return a list of records (which happens for select query)
        """
        allowed_errors = ([] if not allow_errors else
                          ['relation', 'does not exist', 'already exists',
                           'no existe', 'ya existe'])
        with PostgresConnector(db_config) as db:
            try:
                res = db.execute(query, with_as_write=with_as_write)
            except psycopg2.ProgrammingError as error:
                error_msg = utils.get_error_message(error)
                if any([string in error_msg for string in allowed_errors]):
                    logger.warning(
                        'An error ocurred, skipped. %s', error_msg.split('\n')[0])
                    return []
                raise
        return res

    def get_views(self, database):
        db_config = self.db_config
        db_config.update({'db_name': database})
        db_config = utils.odoo2postgres(db_config)
        arch_exists = self.execute_query(
            db_config,
            "select 1 from information_schema.columns where"
            " table_name='ir_ui_view' and column_name='arch'"
        )
        arch_column = 'arch' if arch_exists else 'arch_db'
        sql = """SELECT ir_model_data.module || '.' || ir_model_data.name xml_id, {arch} as arch
            FROM ir_model_data
            JOIN ir_ui_view ON res_id = ir_ui_view.id
            WHERE ir_model_data.model = 'ir.ui.view'
            ORDER BY xml_id;""".format(arch=arch_column)
        views = self.execute_query(db_config, sql)
        return views

    def compare_views(self, original_views, modified_views):
        """
        Compare all the views from views from production with the views from updates and returns
        a proper report

        :param original_views: The views from production database (a copy of course)
        :param modified_views: The views from the db with all changes applied
            (-u all, -u app_module).
        :return: a dict with the added, deleted and updated views. In the case of updated will
            return the diff between the production database and the updates database
        """
        res = {'updated': [], 'added': [], 'deleted': []}
        copy_orig_views = original_views[:]  # to maintain original_views unchanged
        total = len(copy_orig_views)
        for view_modified in modified_views:
            found = False
            ind = 0
            while not found and ind < total:
                if copy_orig_views[ind]['xml_id'] == view_modified['xml_id']:
                    if copy_orig_views[ind]['arch'] != view_modified['arch']:
                        res['updated'].append({
                            'xml_id': copy_orig_views[ind]['xml_id'],
                            'original': copy_orig_views[ind]['arch'],
                            'modified': view_modified['arch']
                        })
                    found = True
                    copy_orig_views.pop(ind)
                    total -= 1
                else:
                    ind += 1   # only in else, when no pop is done in copy_orig_views
            if not found:
                res['added'].append(view_modified)
        for original_view in copy_orig_views:
            res['deleted'].append(original_view)
        return res

    def get_translations(self, database):
        db_config = self.db_config
        db_config.update({'db_name': database})
        db_config = utils.odoo2postgres(db_config)
        translations = self.execute_query(
            db_config,
            """SELECT value,id,name,module FROM ir_translation"""
        )
        return translations

    def compare_translations(self, original_translations, modified_translations):
        """ Compare all the translated fields from two databases and returns a proper report

        :param original_translations: The translations contained in the production
                                      database (copy of course).
        :param modified_translations: The translations contained in the updates database with
                                      all the changes that will be applied in the
                                      production database.
        :return: A dict with the added, updated and removed translations between the production
                 database and the updates database.
        """
        res = {'updated': [], 'added': [], 'deleted': []}
        copy_orig_translations = original_translations[:]  # to maintain original_translations
        total = len(copy_orig_translations)
        for modified_translation in modified_translations:
            found = False
            ind = 0
            while not found and ind < total:
                if copy_orig_translations[ind]['id'] == modified_translation['id']:
                    if copy_orig_translations[ind]['value'] != modified_translation['value']:
                        res['updated'].append({
                            'name': copy_orig_translations[ind]['name'],
                            'module': copy_orig_translations[ind]['module'],
                            'original': copy_orig_translations[ind]['value'],
                            'modified': modified_translation['value']
                        })
                    found = True
                    copy_orig_translations.pop(ind)
                    total -= 1
                ind += 1
            if not found:
                res['added'].append({
                    'name': modified_translation['name'],
                    'module': modified_translation['module'],
                    'value': modified_translation['value']
                })
        for original_translation in copy_orig_translations:
            res['deleted'].append({
                'name': original_translation['name'],
                'module': original_translation['module'],
                'value': original_translation['value'],
            })
        return res

    def get_menus(self, database):
        """ Retrieves all the menus from the provided database

        :param database: Name of the database from where deployv will
                         retrieve all the menus.
        :return: Dictionary containing all the menus from the
                 provided database.
        """
        res = dict()
        db_config = self.db_config
        db_config.update({'db_name': database})
        db_config = utils.odoo2postgres(db_config)
        menu_sql = """SELECT ir_model_data.module || '.' || ir_model_data.name AS xml_id,
                        res_id, ir_ui_menu.name
                FROM ir_model_data
                JOIN ir_ui_menu ON res_id = ir_ui_menu.id
                WHERE ir_model_data.model = 'ir.ui.menu';"""

        tree_sql = """WITH RECURSIVE search_menu(id, parent_id, name, depth, hierarchypath) AS (
            SELECT menu.id, menu.parent_id, menu.name, 1, ppmenu.name || '->' || menu.name
            as hierarchypath
            FROM ir_ui_menu AS menu
            JOIN ir_ui_menu AS ppmenu
            ON menu.parent_id = ppmenu.id
            UNION ALL
                SELECT menu.id, menu.parent_id, menu.name, pmenu.depth + 1,
                    hierarchypath || '->' || menu.name
                FROM ir_ui_menu as menu
                JOIN search_menu as pmenu
                ON menu.parent_id = pmenu.id
            )
            SELECT * FROM search_menu WHERE id = {menu} ORDER BY depth DESC LIMIT 1;"""
        menus = self.execute_query(db_config, menu_sql)
        for menu in menus:
            tree = self.execute_query(db_config, tree_sql.format(menu=menu['res_id']))
            hierarchy = tree[0] if tree else {}
            menu.update({'hierarchypath': hierarchy.get('hierarchypath')})
            res.update({
                menu['xml_id']: menu,
            })
        return res

    def compare_menus(self, original_menus, modified_menus):
        """Compare all the menu items from two json values, obtained from backup database,
        and return a proper report

        :param original_menus: A list of dicts, containing info of original menu items.
        :param modified_menus: A list of dicts, containing info of updated menu items.
        :return: A dict with the added, updated and removed menus between both json values."""
        res = {'updated': [], 'added': [], 'deleted': []}
        for uxml_id in modified_menus:
            if uxml_id in original_menus:
                if original_menus[uxml_id]['name'] != modified_menus[uxml_id]['name']:
                    res['updated'].append({
                        'xml_id': uxml_id,
                        'original': original_menus[uxml_id]['name'],
                        'modified': modified_menus[uxml_id]['name'],
                        'hierarchypath': modified_menus[uxml_id].get('hierarchypath')
                    })
            else:
                res['added'].append({
                    'xml_id': uxml_id,
                    'name': modified_menus[uxml_id]['name'],
                    'hierarchypath': modified_menus[uxml_id].get('hierarchypath')
                })
        for pxml_id in original_menus.keys():
            if pxml_id not in modified_menus:
                res['deleted'].append({
                    'xml_id': original_menus[pxml_id]['xml_id'],
                    'name': original_menus[pxml_id]['name'],
                    'hierarchypath': original_menus[pxml_id].get('hierarchypath')
                })
        return res

    def get_fields(self, database):
        """Gets all the fields from the specified database and returns
            their basic information.

        :param database: name of the database from where the fields will be
            retrieved.
        :return: List of dicts with the information of the fields::
            .. code-block:: json

                    [
                        {
                            'model': model,
                            'name': field,
                            'description': description,
                            'type': field_type \
                        } \
                    ]
        """
        sql = """
        select model, name, field_description as description,
        ttype as type from ir_model_fields;
        """
        db_config = self.db_config
        db_config.update({'db_name': database})
        db_config = utils.odoo2postgres(db_config)
        res = self.execute_query(db_config, sql)
        return res

    def compare_fields(self, original_fields, modified_fields):
        """Compare all the field items from two json values, obtained from backup database,
        and return a proper report

        :param original_fields: A list of dicts, containing info of original fields items.
        :param modified_fields: A list of dicts, containing info of updated fields items.
        :return: A dict with the added, updated and removed fields between both json values."""
        res = {'updated': [], 'added': [], 'deleted': []}
        copy_orig_fields = original_fields[:]  # to maintain original_fields unchanged
        total = len(copy_orig_fields)
        for modified in modified_fields:
            found = False
            ind = 0
            while not found and ind < total:
                if modified['model'] == copy_orig_fields[ind]['model'] \
                        and modified['name'] == copy_orig_fields[ind]['name']:
                    if modified['type'] != copy_orig_fields[ind]['type'] \
                            or modified['description'] != copy_orig_fields[ind]['description']:
                        res['updated'].append({
                            'model': copy_orig_fields[ind]['model'],
                            'name': copy_orig_fields[ind]['name'],
                            'original': {'type': copy_orig_fields[ind]['type'],
                                         'description': copy_orig_fields[ind]['description']},
                            'modified': {'type': modified['type'],
                                         'description': modified['description']},
                        })
                    found = True
                    copy_orig_fields.pop(ind)
                    total -= 1
                ind += 1
            if not found:
                res['added'].append(modified)
        for original_field in copy_orig_fields:
            res['deleted'].append(original_field)
        return res

    def get_odoo_users(self, database, user_id=False):
        """ Retrieves the user ids of all the current users registered in
        the odoo instance.

        :param database: Name of the database where deployv will retrieve
                         the users ids from.
        :param user_id (optional): Id of the user to filter the query.
        :return: List of users ids
        """
        psql_dict = self.db_config
        psql_dict.update({'db_name': database})
        query = psycopg2_sql.SQL("SELECT id,login FROM res_users ")
        if user_id:
            query += psycopg2_sql.SQL("where id={0}").format(psycopg2_sql.Literal(user_id))
        with PostgresConnector(utils.odoo2postgres(psql_dict)) as db:
            users = db.execute(query.as_string(db._PostgresConnector__conn))
        return users

    @staticmethod
    def change_password(user_id, new_pass, db_name, db_config):
        """ Changes the specified user_id password

        :param user_id: Users id
        :param new_pass: New password that will be set to the user
        :param db_name: Database name to be updated
        :return: True if the password was changed, None otherwise
        """
        logger.info('Changing password for user_id %s', user_id)
        default_crypt_context = CryptContext(
            ['pbkdf2_sha512', 'md5_crypt'],
            deprecated=['md5_crypt'],
        )
        db_config.update({'db_name': db_name})
        with PostgresConnector(utils.odoo2postgres(db_config)) as db:
            try:
                res_user = db.execute(("select * from res_users where id = %(id)s"),
                                      {'id': user_id})
            except psycopg2.ProgrammingError as error:
                error_msg = ("Failed to change the password of the user {user}: {error}"
                             .format(user=user_id, error=str(error)))
                logger.error(error_msg)
                return {'error': error_msg}
            res = {"result": True}
            if res_user and res_user[0].get('password_crypt'):
                logger.info('Encrypted password')
                crypted_passwd = default_crypt_context.encrypt(new_pass)
                db.execute(("update res_users set password='',"
                            " password_crypt=%(passwd)s where id = %(id)s"),
                           {'passwd': crypted_passwd, 'id': user_id})
            elif res_user and res_user[0].get('password'):
                logger.info('Non encrypted password')
                db.execute("update res_users set password=%(passwd)s where id = %(id)s",
                           {'passwd': new_pass, 'id': user_id})
        res.update({"result": new_pass})
        return res

    def check_keys(self):
        """ Check if the provided keys into the docker container allows the user to connect
            github.com but does not check permissions

        :return: True if it is a valid key, False otherwise
        """
        logger.info('Checking keys in container %s', self.docker_id)
        res = self.exec_cmd('su {user} -c "ssh -T git@github.com"'
                            .format(user=self.config.get('env_vars').get('odoo_user')))
        if u'successfully authenticated, but GitHub does not provide shell access.' in res:
            logger.info('Keys checked properly')
            return True
        logger.error(
            'An error occurred while trying to connect to github.com: %s', res.strip())
        return False

    def install_deps(self):
        """ Install dependencies specified in the config json (if any). To see the return
        format check :func:`~deployv.base.dockerv.DockerV.install_packages`

        :return: A dic with the installation process
        """
        apt_list = self.config.get('apt_install', None)
        pip_list = self.config.get('pip_install', None)
        res = self.install_packages(apt_list, pip_list)
        return res

    def clean_volumes(self, container_name=False):
        """Removes all the files in the /tmp folder, .ssh directory, in the filestore,
        and the logs inside the container. This method is used to clean the files before
        destroying a container so they are not present the next time we deploy the same container
        """
        logger.info('Cleaning volumes')
        use_snapshot = self.__full_config.backup_type in ['btrfs', 'zfs']
        volumes = self._get_volumes(container_name)
        if not volumes:
            # If `volumes` is empty, its because the container does not exist.
            logger.warning('Container %s does not exist, unable to clean its volumes.',
                           container_name)
            return
        for key, volume in volumes.items():
            if (self.config.get('keep_db') or use_snapshot) and key == 'filestore':
                continue
            logger.info('Removing volume: %s', volume)
            self.exec_cmd('rm -rf {volume}'.format(volume=volume),
                          container_name=container_name)

    def _get_volumes(self, container_name=False):
        # Value used to avoid overwriting a dictionary key if two paths have the same basename
        count = 0
        container_name = container_name or self.config.get('container_name')
        logger.info('Cleaning the volumes of the container: %s', container_name)
        volumes = self.config.get('volumes').copy()
        json_volumes = volumes.values()
        try:
            info = self.inspect(container_name)
        except errors.NoSuchContainer:
            logger.debug('Container %s does not exist, unable to obtain its volumes',
                         container_name)
            return {}
        container_volumes = [volume.get('Destination') for volume in info.get('Mounts')]
        for volume in container_volumes:
            if volume in json_volumes:
                continue
            key = '_volume_%(path_name)s_%(count)s' % {
                'path_name': path.basename(volume), 'count': count}
            count += 1
            volumes.update({key: volume})
        return volumes

    def set_parameters(self, db_name, parameters):
        """Inserts the provided parameters in the ir.config_parameter
        table of the provided database.

        :param db_name: Name of the database where the parameters will be inserted
        :param parameters: Dictionary with the parameters that will be created in the db where
            each key in the dictionary is the name (key) of the parameter and the value of that key
            is the value of that parameter.
        :type parameters: dict
        """
        config = self.db_config
        config.update({'db_name': db_name})
        with PostgresConnector(utils.odoo2postgres(config)) as db:
            for key, value in parameters.items():
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                sql = (
                    "INSERT INTO ir_config_parameter ("
                    "    create_uid, write_date, value, write_uid, key, create_date)"
                    " VALUES (1, '{date}', '{value}', 1, '{key}', '{date}');"
                    .format(value=value, key=key, date=date))
                try:
                    db.execute(sql)
                except (psycopg2.IntegrityError, psycopg2.ProgrammingError) as error:
                    error_msg = utils.get_error_message(error)
                    if 'duplicate key value violates unique constraint' in error_msg:
                        # Remove parameter from the new db and insert it again with the new values
                        db.execute("delete from ir_config_parameter where key = '{key}'"
                                   .format(key=key))
                        db.execute(sql)
                    elif 'does not exist' in error_msg:
                        logger.warning('Failed to set the %s parameter, skipping', key)
                    else:
                        raise
        return True

    def set_global_env_vars(self, rcfile=False):
        """Adds the environment variables specified in the config json to the
            sh rc file so all users that connect to the instance can use them.

        :param rcfile: full path to the rc file where the env vars will be set
            (bash.bashrc, zshrc, etc), if no path is specified /etc/bash.bashrc will be used
        :type rcfile: str

        """
        env_vars = []
        if not rcfile:
            rcfile = '/etc/bash.bashrc'
        for var, value in self.config.get('env_vars', {}).items():
            var_string = 'export {var}={value}'.format(var=var.upper(), value=value)
            env_vars.append(var_string)
        vars_string = "bash -c \"echo -e '{env_vars}' | tee -a {rcfile}\"".format(
            env_vars='\n'.join(env_vars), rcfile=rcfile)
        self.exec_cmd(vars_string)

    def restart_instance(self):
        res = {}
        logger.info('Restarting instance: %s %s',
                    self.__full_config.instance_config.get('task_id'),
                    self.__full_config.instance_config.get('customer_id'))
        retries = 0
        # Restart instance and check if it's running
        try:
            # Check if supervisor is running
            supervisor_status = self.check_supervisor()
            if not supervisor_status:
                res.update({'error': ('Failed to restart the instance: Supervisor'
                                      ' process could not start')})
                return res
            self.exec_cmd('supervisorctl stop ' + self.supervisor_group)
            # Check if odoo was successfully stopped
            while retries <= 3:
                python_process = self.exec_cmd('pgrep python -a').split('\n')
                odoo_process = [process for process in python_process if 'odoo' in process]
                if not odoo_process:
                    break
                logger.info('waiting for the odoo process to stop')
                retries += 1
                time.sleep(20)
            if self.is_running or odoo_process:
                state = self.exec_cmd('supervisorctl status odoo')
                res.update({
                    'error': 'Failed to restart the instance, could not stop odoo'})
                return res
            self.exec_cmd('supervisorctl start ' + self.supervisor_group)
            if not self.is_running:
                state = self.exec_cmd('supervisorctl status ' + self.supervisor_app)
                res.update({
                    'error': ('Failed to restart the instance, could not'
                              ' start odoo: {state}').format(state=state.strip())})
                return res
        except (errors.SupervisorStatusError, errors.CommandError, errors.NotRunning) as error:
            res.update({'error': 'Couldn\'t restart the instance, {error}'.format(
                error=utils.get_error_message(error))})
            return res
        res.update({'result': 'Instance successfully restarted'})
        logger.info('Done')
        return res

    def restart_container(self):
        # Get the information of the container
        pg_shell = PostgresShell(utils.odoo2postgres(self.db_config))
        try:
            container_info = self.basic_info
        except errors.NoSuchContainer:
            logger.error('Failed to restart the container, it does not exist')
            return False
        # Restart container
        try:
            logger.info('Stopping container %s', container_info.get('name'))
            container_obj = self.cli2.containers.get(container_info.get('Id'))
            container_obj.stop()
            logger.info('Terminating connections on the database %s', self.db_config['db_name'])
            pg_shell.terminate_sessions(
                self.db_config['db_name'], self.db_config.get('db_owner'),
                self.db_config.get('db_owner_passwd')
            )
            logger.info('Starting container %s', container_info.get('name'))
            container_obj.start()
        except APIError:
            logger.error('Failed to restart the container, it took to long to start/stop')
            return False
        # Get the container object again so it gets the updated state and
        # check if it is running
        container_obj = self.cli2.containers.get(container_info.get('Id'))
        retries = 0
        while retries <= 3:
            if container_obj.status == 'running':
                return True
            time.sleep(5)
            retries += 1
        # If the while loop ends, that means the container failed to start
        logger.error('Failed to restart the container, state: %s', container_obj.status)
        return False

    def extras_deactivate(self, extra_config=False):
        """Method find the files deactivate.sql that is into of the repositories
        of the container and return a dict with the queries
        """
        res = {}
        extra_config = extra_config or {}
        env_vars = self.config.get('env_vars') or self.docker_env
        odoo_home = env_vars.get('odoo_home')
        env_vars.update(extra_config)
        cmd = "find {0}/instance -name 'deactivate.jinja'".format(odoo_home)
        wf_path = self.__full_config.working_folder
        name = path.basename(wf_path)
        try:
            res_cmd = self.exec_cmd_image(cmd, {name: '/tmp'}, wf_path)
        except errors.CommandError:
            return res
        if not res_cmd.get('result') or 'No such file or directory' in res_cmd.get('result'):
            logger.info('Could not find the deactivate.jinja file in %s', odoo_home)
            return res
        if res_cmd.get('error'):
            return res_cmd
        for file_sql in res_cmd['result'].splitlines():
            if not file_sql:
                continue
            sqls = self.exec_cmd_image("cat {0}".format(file_sql), {name: '/tmp'}, wf_path)
            if sqls.get('error'):
                logger.error(sqls.get('error'))
                res.update(sqls)
                return res
            sql_json = json_helper.load_json(Template(sqls['result']).render(**env_vars))
            res.update(sql_json or {})
        return res

    def start_maintenance_page_container(self):
        """Starts the container that will be used while the production
        instance is updated. This container will be created with an image
        that will serve a custom page or app, and will be destroyed after the
        update is done.
        """
        logger.info('Starting maintenance page\'s container')
        ports = {'80': self.config.get('ports').get('8069')}
        container_config = {
            "name": (
                '%(customer_id)s_maintenance_page' % {
                    'customer_id': self.__full_config.instance_config.get('customer_id')
                }
            ),
            "image": self.__full_config.maintenance_page.get("image_name"),
            "hostname": container.generate_hostname(self.__full_config),
            "ports": container.generate_port_lists(ports),
            "environment": container.generate_env_vars(
                self.__full_config.maintenance_page.get("env_vars")
            ),
        }
        host_config = {
            "port_bindings": container.generate_port_bindings(ports),
            "mem_limit": self.config.get("mem_limit", 0),
            "memswap_limit": self.config.get("mem_limit", 0),
            "restart_policy": {
                "MaximumRetryCount": 0,
                "Name": "unless-stopped"
            }
        }
        hconfig = self.cli.create_host_config(**host_config)
        container_obj = self.cli.create_container(
            host_config=hconfig, **container_config
        )
        container_id = container_obj.get("Id")
        logger.info('Container created %s', container_id)
        logger.info('Starting container %s', container_id)
        self.cli.start(container=container_id)
        logger.info('Container started %s', container_id)
        return container_id

    def create_vx_schema(self, db_config):
        """Create vx schema and required functions to anonymize data
        :return: boolean, error_message (True when process is successful)"""
        try:
            self.execute_query(
                db_config, "CREATE SCHEMA vx; SECURITY LABEL FOR anon ON SCHEMA vx IS 'TRUSTED';")
        except Exception as e:
            error = utils.get_error_message(e)
            logger.error('Error while create vx schema, and set security label: %s', error)
            return False, error
        queries = pg_anon.get_queries_vx_functions()
        try:
            self.execute_query(db_config, queries)
        except Exception as e:
            error = utils.get_error_message(e)
            logger.error('Error while create functions in vx schema: %s', error)
            return False, error
        return True, ''

    def anonymize_db(self, db_config):
        """Apply masked functions to anonymize some data, as indicated by config file.
        Verify that postgresql anonymizer is installed, otherwise, try to install it.

        :param db_config: Configuration for database where the query will be executed
        :return: boolean, error_message (True when process is successful)"""
        # verify if postgresql anonymizer extension is available
        res = self.execute_query(
            db_config, "SELECT name, installed_version FROM pg_catalog.pg_available_extensions "
                       "WHERE name='anon'")
        if res:
            if res[0]['installed_version'] is None:
                query = "ALTER DATABASE {} SET session_preload_libraries = 'anon';".format(
                    db_config['dbname'])
                try:
                    self.execute_query(db_config, query)
                except Exception as e:
                    error = utils.get_error_message(e)
                    logger.error('Error while set anon extension: %s', error)
                    return False, 'Anonymizer error: {}'.format(error)
                query = "CREATE EXTENSION anon CASCADE; SELECT anon.init(); " \
                        "ALTER DATABASE {} SET anon.restrict_to_trusted_schemas = on;" \
                    .format(db_config['dbname'])
                try:
                    self.execute_query(db_config, query)
                except Exception as e:
                    error = utils.get_error_message(e)
                    logger.error('Error while create anon extension: %s', error)
                    return False, 'Anonymizer error: {}'.format(error)

            res = self.execute_query(db_config,
                                     "SELECT COUNT(*) as qty FROM pg_catalog.pg_namespace "
                                     "WHERE nspname='vx';")
            if not res[0]['qty']:
                res, error = self.create_vx_schema(db_config)
                if not res:
                    return res, 'Anonymizer error: {}'.format(error)

            queries = pg_anon.get_queries_from_operations_file(
                '/etc/deployv/deactivate/anon_operations.csv')
            for item in queries:
                try:
                    self.execute_query(db_config, item)
                except Exception as e:
                    error = utils.get_error_message(e)
                    logger.error('Error while executing anonymize data query: %s', error)
                    return False, 'Anonymizer error: {}'.format(error)
            return True, ''
        logger.error('Extension postgresql anonymizer is not available')
        return False, 'Anonymizer error: Extension postgresql anonymizer is not available'

    def deactivate_database(self, db_name, extra_config=False):
        """Executes the deactivation queries found in the deactivation.jinja file
        on the provided database.

        :param db_name: Name of the database where the queries will be executed
        :param extra_config: Dictionary with the additional config used to
            render the deactivation.jinja file

        :return: Error message when data anonymization fails, None otherwise
        """
        logger.info('Deactivating database %s', db_name)
        if self.docker_id:
            self.stop_instance()
        db_config_user = self.db_config.copy()
        db_config_user.update({'db_name': db_name})
        db_config_owner = db_config_user.copy()
        db_config_owner.update({
            'db_user': self.db_config.get("db_owner"),
            'db_password': self.db_config.get('db_owner_passwd')
        })
        db_config_user = utils.odoo2postgres(db_config_user)
        db_config_owner = utils.odoo2postgres(db_config_owner)
        # executes anonymization, if required
        if path.isfile('/etc/deployv/deactivate/anon_operations.csv'):
            logger.info('Start anonymization of data')
            res, error_msg = self.anonymize_db(db_config_user)
            if res:
                logger.info('Successful anonymization of data')
            else:
                logger.exception('Failed anonymization of data')
                postgres = PostgresShell(utils.odoo2postgres(self.db_config.copy()))
                postgres.drop(db_name)
                return {'error': error_msg}
        extra_config = extra_config or {}
        extra_sqls = self.extras_deactivate(extra_config)
        if extra_sqls.get('error'):
            logger.error(extra_sqls.get('error'))
            return extra_sqls
        query_config = ("select id from ir_model_fields where name"
                        "= 'value' and model = 'ir.config_parameter';")
        config_parameter_id = self.execute_query(db_config_user, query_config)
        config_parameter_id = config_parameter_id and config_parameter_id[0].get('id')
        # Obtain the crons that will not be deactivated
        action_ids = []
        try:
            query_res = self.execute_query(
                db_config_user,
                "select id from ir_act_server where model_name = 'ir.autovacuum';")
            action_ids = [result.get('id') for result in query_res]
        except psycopg2.errors.UndefinedColumn as error:
            logger.warning('Unable to deactivate the crons, using legacy deactivate method: %s',
                           error.pgerror)
        # Parameters to render the template
        extra_config.update({
            'field_id': config_parameter_id, 'uuid': uuid4(),
            'migration': self.__full_config.migration,
            'action_ids': action_ids,
        })
        # Sqls to be executed
        template_path = deployv_static.get_template_path('deactivation.jinja')
        with open(template_path, 'r') as obj:
            json_template = obj.read()
        sqls = json_helper.load_json(Template(json_template).render(extra_config))
        # Load the demo pac
        certificate_pac = utils.get_certificates_pac()
        sql = "UPDATE l10n_mx_edi_certificate SET "
        sql += " ,".join(["%s='%s'" % (k, v) for k, v in certificate_pac.items()])
        sqls.update({"mx_edi_certificate": sql})
        sqls.update(extra_sqls)
        customer_id = self.__full_config.instance_config.get("customer_id")
        customers_exclude = self.__full_config.deployer.get('ignore_timeout_deactivate', [])
        # Start to execute the queries
        try:
            for name in sorted(sqls):
                logger.debug('Running %s', name)
                sql = sqls[name]
                try:
                    self.execute_query(db_config_user, sql, allow_errors=True, with_as_write=True)
                except psycopg2.errors.InsufficientPrivilege as error:
                    logger.warning("Insufficient permissions for user '%s': %s",
                                   db_config_user.get('user'), utils.get_error_message(error))
                    self.execute_query(db_config_owner, sql, allow_errors=True)
                except psycopg2.errors.QueryCanceled as error:
                    if customer_id in customers_exclude:
                        logger.warning("Timeout executing query: %s", sql)
                    else:
                        raise error
        except psycopg2.OperationalError as error:
            if hasattr(error, 'pgerror'):
                message = error.pgerror
            else:
                message = error.message
            logger.exception('Could not deactivate the database: %s', message)
        return {}

    @property
    def db_config(self):
        """ Parse env vars from a container to get the needed parameters to dump the database

        :return: dict with the needed configuration parameter
        """

        env_vars = self.docker_env or {}
        if self.__full_config.backup_type in ['btrfs', 'zfs']:
            env_vars = env_vars or self.config.get('env_vars')
        res = self.__full_config.instance_config.get("config").copy()
        logger.debug(json.dumps(env_vars, sort_keys=True, indent=4))
        logger.debug("Instance config dict from json: %s", str(res))
        res.update({
            'db_host': res.get('db_host') or env_vars.get('db_host') or '127.0.0.1',
            'db_port': env_vars.get('external_db_port') or res.get(
                'db_port') or env_vars.get('db_port') or 5432,
            'db_user': res.get('db_user') or env_vars.get('db_user'),
            'db_password': res.get('db_password') or env_vars.get('db_password'),
            'data_dir': self.get_data_dir()
        })
        docker_network_info = self.cli.inspect_network('bridge')
        docker_gateway = docker_network_info.get('IPAM').get('Config')[0].get('Gateway')
        is_docker_ip = utils.is_docker_ip(res.get('db_host'), docker_gateway)
        if ((is_docker_ip or res.get('db_host') == 'localhost') and not
                self.__full_config.deployer.get('deployv_in_docker')):
            res.update({'db_host': '127.0.0.1'})
        return res

    def get_data_dir(self):
        """Return the path where store the filestore inside of container.
        """
        try:
            inspected = self.inspect()
        except errors.NoSuchContainer:
            return ''
        for volume in inspected.get('Mounts', []):
            if volume and '.local/share/Odoo' in volume.get('Destination'):
                return volume.get('Source')
        logger.error('Datadir not found, wont be able to backup attachments')

    def save_repositories(self, filename=False):
        """Save the repositories stored in the image name.
        that information is saved in the specify path.

        :param file_name: The file's name where the repositories's information are saved.
        :type: str
        """
        self.exec_cmd('pip3 install branchesv')
        if not self.temp_folder:
            logger.warning("Save Repositories: Doesn't exist a temp folder where save the file")
            return ''
        home = self.__full_config.container_config.get('env_vars').get('odoo_home')
        odoo_user = self.__full_config.container_config.get('env_vars').get('odoo_user')
        filename = filename or 'branches.json'
        self.exec_cmd('bash -c "rm -rf /tmp/%s"' % (filename))
        cmd = 'bash -c "branchesv save -p %s/instance -f /tmp/%s"' % (home, filename)
        file_path = path.join(self.temp_folder, filename)
        cmd_output = self.exec_cmd(cmd)
        logger.debug('Branchesv result:\n%s', cmd_output)
        if not path.exists(file_path):
            cmd = 'su %s -c "branchesv save -p %s/instance -f /tmp/%s"' % (
                odoo_user, home, filename)
            cmd_output = self.exec_cmd(cmd)
            logger.debug('Branchesv result:\n%s', cmd_output)
        return file_path

    @property
    def config_variables(self):
        """Property to get the value of variables from this Class or
        get the information from the docker environment.
        Then if the `BASE_IMAGE`, `PSQL_VERSION`, `TRAVIS_PYTHON_VERSION`, `ODOO_REPO` or
        `ODOO_BRANCH` keys doesn't exist, it will set default values according to the version.
        """
        docker_env = self.docker_env or {}
        variables = self.__full_config.variables or docker_env
        if self.__full_config.container_config.get('env_vars'):
            variables.update(self.__full_config.container_config.get('env_vars'))
        main_repo = [r for r in self.__full_config.instance_config.get('repositories')
                     if r.get('main_repo')]
        if docker_env.get('main_app'):
            variables.update({'main_app': docker_env.get('main_app')})
        if not variables.get('version') and main_repo:
            variables.update({'version': main_repo[0].get('branch')})
        version = variables.get('version') or ''
        default_variables = {
            'base_image': 'vauxoo/odoo-%s-image' % (version.replace('.', '')),
            'psql_version': PSQL_VERSIONS.get(version),
            'travis_python_version': TRAVIS_VERSIONS.get(version),
            'odoo_repo': 'vauxoo/odoo', 'odoo_branch': version
        }
        for key, value in default_variables.items():
            if not variables.get(key) and value:
                variables.update({key: value})
        return variables

    def _get_db_manifest(self, tmp_dir):
        """ Generates a manifest with the information of the modules installed in the database
        to be added in the backups, just like the one added by odoo in its backups.
        """
        db_config = self.db_config
        with PostgresConnector(utils.odoo2postgres(db_config)) as db:
            try:
                installed_modules = db.execute(
                    "SELECT name, latest_version FROM ir_module_module WHERE state = 'installed'",
                    raw=True
                )
                version = db.execute("SELECT current_setting('server_version_num');")
            except psycopg2.ProgrammingError as error:
                error_msg = utils.get_error_message(error)
                logger.error('An error ocurred while obtaining the dump manifest: %s', error_msg)
                raise errors.CommandError('backup', error_msg)
        version = int(version[0].get('current_setting'))
        manifest = {
            'odoo_dump': 1,
            'db_name': db_config.get('db_name'),
            'pg_version': "%d.%d" % divmod(version / 100, 100),
            'modules': dict(installed_modules)
        }

        # Instances that use python3 have python2 as default, that version does not have
        # odoo's requirements so it raises an error when we try to execute this script,
        # so we need to check which python version to use. It's done by checking if
        # python3 exists instead of checking which version of odoo is running to avoid
        # having to update the list with each new version of odoo.
        python3_exists = self.exec_cmd('ls /usr/bin/python3')
        pybin = 'python' if 'No such file or directory' in python3_exists else 'python3'
        cmd = '{pybin} /tmp/get_release_data.py'.format(pybin=pybin)
        release_data = self.exec_cmd(cmd)

        # Backwards compatibility condition, only the new images will have this script
        # so we will create it manually if the container does not have it yet. This
        # block needs to be removed in the future.
        if 'No such file or directory' in release_data:
            script = """
import sys

sys.path.insert(1, '/home/odoo/instance/odoo')
from odoo import release
import simplejson as json

print(json.dumps({
    'version': release.version,
    'major_version': release.major_version,
    'version_info': release.version_info}))
            """
            with open(path.join(self.temp_folder, 'get_release_data.py'), 'w') as obj:
                obj.write(script)
            release_data = self.exec_cmd(cmd)

        # Parse release data obtained from the script
        parsed_data = json_helper.load_json(release_data)
        # When this method is called by an external tool (e.g. a script), the parsed data
        # cannot be obtained because it may not send the complete container information,
        # returning False in the method above and raising an error when we try to update
        # the response.
        manifest.update(parsed_data or {})
        manifest_path = path.join(tmp_dir, 'manifest.json')
        json_helper.save_json(manifest, manifest_path)
        return manifest_path

    def create_extension_unaccent(self, db_name):
        """ Logs into postgres as a superuser in order to create the
        unaccent extension.

        :param db_name: name of the database where the extension will
            be created.
        """
        pg_shell = PostgresShell(self._get_admin_config())
        pg_shell.create_extension_unaccent(db_name)

    def _get_admin_config(self):
        admin_config = self.db_config.copy()
        admin_config.update({
            'db_user': self.__full_config.postgres.get('db_user'),
            'db_password': self.__full_config.postgres.get('db_password'),
        })
        return utils.odoo2postgres(admin_config)

    def update_info_postgres_container(self):
        """Update the env_vars with the port and host where is running the Postgres container.
        """
        destination = '/var/log/pg_log'
        if self.config.get('keep_db') or self.__full_config.reloading_config:
            info = self.inspect(self.config.get('postgres_container_name'))
            db_host = info.get('NetworkSettings').get('Gateway')
            self.config.update({'pg_log_postgres': self.get_specify_volumen(info, destination)})
            db_port = self.get_db_port(info)
            self.__full_config.instance_config.get("config").update({
                'db_host': db_host, 'db_port': db_port})
            self.config.get('env_vars').update({
                'db_port': db_port,
                'db_host': db_host, 'external_db_port': db_port})
            return True
        return False


class DummyInstanceV:

    def __init__(self, config, timeout=False, docker_url=False):
        super(DummyInstanceV, self).__init__()
