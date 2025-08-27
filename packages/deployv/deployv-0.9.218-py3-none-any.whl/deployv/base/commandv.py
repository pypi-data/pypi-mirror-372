# coding: utf-8

"""This class has the algorithms that will be executed by deployvcmd and deployvd, both are
interfaces between the input (files, cmd interface and rabbitmq) and CommandV.

`extend_me <http://pythonhosted.org/extend_me/>`_ is used in the event manager class and the core
command component because it allows an easy app extension without the need of modifying the core
components.

CommandV inherits from `Extensible <http://pythonhosted.org/extend_me/#extensible>`_ base class so
it can be extended in a simple way by just inheriting from CommandV.
"""

import logging
import os
import re
import requests_unixsocket
import yaml
import simplejson as json
import base64
import deployv_static
from extend_me import Extensible
from psycopg2 import OperationalError
from datetime import datetime
from docker import from_env
from docker.errors import APIError, NullResource, NotFound, ImageNotFound
from deployv.base.extensions_core import events, load_extensions
from deployv.base import postgresv, nginxv, errors, clonev
from deployv.helpers import (utils, container, database_helper, sender_message,
                             build_helper, json_helper, git_helper)
from deployv.instance import instancev
from deployv.extensions.checkers import InstallTestRepo
from transitions import State, Machine
from tempfile import mkdtemp

logger = logging.getLogger(__name__)  # pylint: disable=C0103

load_extensions()


STATES = [
    'Starting',
    State('Building commit history'),
    State('Building image'),
    State('Creating container'),
    State('Deactivating database'),
    State('Restoring backup'),
    State('Restoring btrfs backup'),
    State('Restoring zfs backup'),
    State('Generating backup'),
    State('Generating btrfs backup'),
    State('Generating zfs backup'),
    State('Deactivating backup'),
    State('Changing passwords'),
    State('Updating database'),
    State('Destroying instance'),
    State('Destroying btrfs instance'),
    State('Destroying zfs instance'),
    State('Pushing images'),
    State('Updating production instance'),
    State('Restarting container'),
    State('Restarting instance'),
    State('Executing final steps'),
    'Done', 'Error'
]


class CommandV(Extensible):
    """ Class that contains the main methods of each command

    :param config: Configuration dictionary. See :class:`~deployv.base.instancev.InstanceV`.
    :type config: dict
    :param instance_class: Class for the instance manager object.
    :type instance_class: class
    """

    def __init__(self, config_obj, instance_class=None):
        self.__config = config_obj
        self._domains = None
        self.sender = sender_message.SenderMessage(self.__config)
        transitions_path = deployv_static.get_template_path('transitions.json')
        transitions = json_helper.load_json(transitions_path)
        self.process = Machine(model=self, states=STATES, transitions=transitions,
                               initial='Starting')
        self._update_done = False
        self._need_revert = False
        if self.__config.instance_config:
            prefix = container.generate_prefix(self.__config)
            self.__config.prefix = prefix and prefix.lower()
        if instance_class:
            self.__instance_manager = instance_class(self.__config)
        else:
            self.__instance_manager = instancev.InstanceV(self.__config, timeout=3000)
        self.create_working_folder()

    @property
    def instance_manager(self):
        return self.__instance_manager

    def deactivating_database(self):
        """Transitions condition used to take the process setps required to
        deactivate a database. This method only returns True if the
        deactivate command is called or if the `deactivating_database`
        parameter is specified in the config json > group_config dictionary.
        """
        return self.__config.deactivating_database or False

    def pushing_images(self):
        """Transitions condition used to finish the process after pushing
        the images. This condition was only added in order to keep the
        posibility to create a `push` command.
        """
        return self.__config.pushing_images or False

    def create_database(self):
        """Transitions condition used to add the `restore` command to
        the process. This method returns the value stored in the
        config json > instance > restore_db key.
        """
        use_snapshot = self.use_zfs() or self.use_btrfs()
        if self.__config.reloading_config or (
                self.__config.container_config.get('keep_db') and not use_snapshot):
            return False
        return self.__config.instance_config.get('restore_db') or False

    def need_revert(self):
        """Transitions condition used to go to the `Create container` state
        if an error occurs, only used during the `update_production` command
        to revert the changes if an error occurs when the production databases
        are updated.
        """
        return self._need_revert or False

    def deactivate_required(self):
        """Transitions condition used to add the `deactivate` step to the
        process. This method only returns True if the
        config json > instance > instance_type key is any of `updates`,
        `develop`, or `test`.
        """
        instance_type = self.__config.instance_config.get('instance_type')
        if instance_type in instancev.DEACTIVATE:
            return True
        return False

    def update_required(self):
        """Transitions condition used to add the `update` step to the process.
        This method only returns True if the
        config json > instance > instance_type key is `updates` or `develop`.
        """
        instance_type = self.__config.instance_config.get('instance_type')
        if self._update_done or instance_type == 'test':
            return False
        if instance_type in instancev.UPDATE or self.__config.container_config.get('keep_db'):
            InstallTestRepo.event = 'after.updatedb.event'
            return True
        return False

    def deactivating_backup(self):
        """Transitions condition used to take the process setps required to
        deactivate a backup. This method only returns True if the
        deactivate_backup command is called or if the `deactivating_backup`
        key is specified in the config json > group_config dictionary.
        """
        return self.__config.deactivating_backup or False

    def build_image_required(self):
        """Transitons condition used to add the `build_image` step to
        the process. This only returns True if either the `build_image` or
        `full_stack` keys in config json > container_config are True.
        """
        cfg = self.__config.container_config
        return cfg.get('build_image') or cfg.get('full_stack') or False

    def skip_push(self):
        """Transitions condition used to skip the `push_images` step during
        the process in order to avoid pushing the full stack images, this is
        also used to willingly skip the push during a process. The condition
        is True if the config json > container_config > `full_stack` or the
        config json > group_config > skip_push keys are True.
        """
        return self.__config.container_config.get('full_stack') or self.__config.skip_push

    def create_container(self):
        """Transitions condition used to add the `create container` step to
        the process. This method only returns True if the `create` command
        is called or if the config json > group_config > create_container key
        is True.
        """
        return self.__config.create_container or False

    def updating_instance(self):
        """Transitions condition used to take the process steps required to
        update an instance from orchest.
        """
        return self.__config.updating_instance

    def keep_database(self):
        """Transitions condition used to know where keep the database or
        the instance is updating and continue with the deactivation of database.
        """
        if self.__config.reloading_config:
            return False
        return self.__config.container_config.get('keep_db') or self.__config.updating_instance

    def is_production(self):
        """Transition condition, used to know if instance to deploy is production or not"""
        return self.__config.instance_config.get('instance_type') == 'production'

    def reloading_config(self):
        """Transitions condition used to know which steps to take when reloading
        a container's config.
        """
        return self.__config.reloading_config or False

    def use_btrfs(self):
        """Transtions condition used to know how to handle the databases (delete, restore, backup)
        """
        instance_type = self.__config.instance_config.get('instance_type')
        return self.__config.backup_type == 'btrfs' and instance_type != 'production'

    def use_zfs(self):
        """Transtions condition used to know how to handle the databases (delete, restore, backup)
        """
        instance_type = self.__config.instance_config.get('instance_type')
        return self.__config.backup_type == 'zfs' and instance_type != 'production'

    def container_created(self):
        """Transitions condition used to know if the Odoo server is created.
        """
        if self.__instance_manager.docker_id:
            return True
        return False

    def test_instance_created(self):
        """Transitions condition used to go to the `Executing final steps` state
        when is a test instance and the state before is `Creating container`
        """
        instance_type = self.__config.instance_config.get('instance_type')
        return self.container_created() and instance_type == 'test'

    def _can_add_new(self, container_name=''):
        """As we have a limited amount of resources in each node we need to check if the running
        instances count is less than the allowed to run a new one.

        :returns: If the count of running instances is lower than the allowed max.
        :rtype: bool
        """
        # container_names is required due to result obtained from cli.containers()
        if container_name:
            container_names = [container_name, '/' + container_name]
        else:
            container_names = []
        containers = self.instance_manager.cli.containers()
        max_instances = self.__config.deployer.get('max_instances')
        if not max_instances:
            return True
        count = 0
        for container_info in containers:
            for name in container_info.get('Names'):
                if re.match(r'/([\w\d\_\-\.]+)_odoo$', name) and name not in container_names:
                    count += 1
                    break
        logger.debug('Instance count %s/%s', count, max_instances)
        return count < max_instances

    def build_image(self):
        """Builds a new image using the configuration in the json
        and returns the name of the image built as well as the first 10
        characters of it's sha.

        :return: Dictionary with the `image_name` and `image_sha` keys
        """
        metrics = {'statuses': ['create', 'total_process'], 'stage': 'started'}
        self.sender.send_result(log='Building image', metrics=metrics)
        res = {'command': 'build_image'}
        self.__config.check_config('build_image')
        if self.__config.container_config.get('build_image'):
            clone_res = clonev.CloneV(self.__config, self.instance_manager).clone_repositories()
            if clone_res.get('error'):
                res.update(clone_res)
                self.send_message_error(res, ['create', 'total_process'])
                return res
        build_res = build_helper.build_image(self.__config, self.instance_manager.config_variables)
        logger.debug('Build res %s', res)
        res.update(build_res)
        if res.get('error'):
            self.send_message_error(res, ['create', 'total_process'])
            return res
        image_name = res.get('result').get('image_name')
        self.sender.send_result(log='Image %s built' % image_name)
        base_img = self.__config.container_config.get('customer_image')
        if self.instance_manager.config_variables.get('docker_image_repo'):
            base_img = self.instance_manager.config_variables.get('docker_image_repo')
            tag_img = '{app}-{version}-{sha}'.format(
                app=self.instance_manager.config_variables.get('main_app'),
                version=self.instance_manager.config_variables.get('version'),
                sha=res['result'].get('image_sha'))
        else:
            logger.warning('*** *** *** WARNING *** *** ***')
            logger.warning('You are using a legacy mode for tag docker images.'
                           'New mode requires set docker_image_repo environment variable.')
            logger.warning('*** *** *** *** *** *** *** ***')
            tag_img = res['result'].get('image_sha')
        full_image_name = '{img}:{tag}'.format(img=base_img, tag=tag_img)
        if not isinstance(self.__config.container_config.get('push_image'), list):
            self.__config.container_config.update({'push_image': []})
        instance_type = self.__config.instance_config.get('instance_type')
        self.__config.container_config.get('push_image').append({
            'tag': tag_img, 'base': base_img,
            'image': res.get('result').get('image_name'),
            'tag_latest': bool(instance_type == 'updates')})
        self.__config.container_config.update({
            'image_name': (full_image_name if not self.skip_push() else
                           res.get('result').get('image_name'))
        })
        self.build_done_trigger()
        return res

    @events
    def create(self):
        """Creates an Odoo dockerized instance with the provided configuration.

        :returns: A response in json format containing the info dict returned
            by :func:`~deployv.base.dockerv.DockerV.basic_info`.
        :rtype: dict
        """
        res = {'command': 'create' if not self.reloading_config() else 'reload_config',
               'result': {}, 'attachments': list()}
        metrics = {'statuses': ['create', 'total_process'], 'stage': 'started'}
        self.sender.send_result(log='Creating instance', metrics=metrics)
        self.__config.check_config('create')
        container_name = self.__config.container_config.get('container_name')
        if not self._can_add_new(container_name):
            logger.info('Max instance count reached (%s allowed)',
                        self.__config.deployer.get('max_instances'))
            res.update({'error': 'Reached max instance count for this node ({} allowed)'
                       .format(self.__config.deployer.get('max_instances'))})
            self.send_message_error(res, ['create', 'total_process'])
            return res
        try:
            info = self.instance_manager.start_odoo_container()
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.exception('Could not start container')
            res.update({'error': utils.get_error_message(error)})
            self.send_message_error(res, ['create', 'total_process'])
            return res
        if info.get('error'):
            res.update({'error': info.get('error')})
            self.send_message_error(res, ['create', 'total_process'])
            return res
        post_branch = self.instance_manager.save_repositories('post_process.json')
        res.get('attachments').append(
            {
                'file_name': os.path.basename(post_branch),
                'file': utils.generate_attachment(post_branch),
                'type': 'application/json'
            }
        )
        if info:
            res.get('result').update(info)
            if self.__config.deployer:
                logger.debug('Use nginx config: %s',
                             self.__config.deployer.get('use_nginx', False))
                if self.__config.deployer.get('use_nginx', False):
                    logger.debug('Using nginx')
                    self._domains = self.update_nginx()
                    nginx_url = self._get_nginx_url(info.get('name')[:-5].replace('_', '-'))
                    url_with_http = "http://{url}".format(url=nginx_url)
                    res['result'].update({
                        'nginx_url': url_with_http,
                        'instance_log': '{url}/logs/odoo_stdout.log'.format(url=nginx_url)
                    })
                    self.instance_manager.config.update({'nginx_url': url_with_http})
        params = self.__config.instance_config.get('restore_filestore')
        if params:
            filestore_res = self.__instance_manager.restore_filestore(
                params.get('path'), params.get('db_name'))
            if filestore_res.get('error'):
                res.update({'error': filestore_res.get('error')})
                self.send_message_error(res, ['create', 'total_process'])
                return res
        self.instance_manager.start_instance()
        res.update({'instance_revert': self._need_revert})
        metrics = {'statuses': ['create'], 'stage': 'finished'}
        self.sender.send_result(res, 'Instance created', metrics=metrics)
        self.create_done_trigger()
        return res

    def _get_nginx_url(self, name):
        nginx_url = None
        for domain in self._domains:
            if domain.get('domain').startswith(name):
                nginx_url = "{domain}.{server}".format(
                    domain=domain.get('domain'), server=self.__config.deployer.get('domain'))
                break
        logger.debug('Updating url : %s', nginx_url)
        return nginx_url

    def deactivate(self, database=False):
        db_config = self.instance_manager.db_config
        database = database or db_config.get('db_name')
        self.sender.send_result(log='Deactivating database %s' % (database))
        self.__config.check_config('deactivate')
        extra_config = {
            'nginx_url': self.instance_manager.config.get('nginx_url'),
            'use_mailhog': self.__config.instance_config.get("use_mailhog")}
        deactivate_res = self.instance_manager.deactivate_database(database, extra_config)
        if deactivate_res.get('error'):
            self.instance_manager._skip_install_test_ribbon = True
            self.send_message_error(deactivate_res)
            return deactivate_res
        new_admin = db_config.get('admin', False)
        if new_admin:
            db_config.update({'db_name': database})
            admin_id = self.get_admin_id(db_config=db_config)
            instancev.InstanceV.change_password(admin_id, new_admin, database, db_config)
        # Start Odoo after deactivated the instance.
        if self.__instance_manager.docker_id:
            self.__instance_manager.start_instance()
        self.sender.send_result(log='Database %s deactivated.' % (database))
        self.deactivate_done_trigger()

    def get_admin_id(self, db_config=False):
        """In Odoo versions > 11.0 user_admin_id = 2 and not 1"""
        db_config = db_config or self.instance_manager.db_config
        cfg = utils.odoo2postgres(db_config)
        with postgresv.PostgresConnector(cfg) as conn:
            admin_users = conn.execute(
                "select id from ir_model_data where name in"
                " ('user_root', 'user_admin');")
        return 2 if len(admin_users) > 1 else 1

    def post_process(self):
        """Command in charge of performing the steps required after deploying an instance
        like generating the cloc report.

        :returns: dict with the results or the errors
        """
        metrics = {'statuses': ['post_process'], 'stage': 'started'}
        self.sender.send_result(log='Executing final steps', metrics=metrics)
        res = {'command': 'post_process'}
        post_process = ['cloc_report', 'list_packages', 'odoo_cloc_report']
        if (self.__config.instance_config.get('instance_type') == 'updates' and
                self.__config.instance_config.get('auto_compare')):
            post_process.append('compare_databases')
        for command in post_process:
            if not hasattr(self, command):
                msg = 'Command {} does not exist, skipping from the post process'.format(command)
                logger.error(msg)
                self.sender.send_result(log=msg, log_type='ERROR')
                continue
            cmd_method = getattr(self, command)
            cmd_res = cmd_method()
            if 'error' in cmd_res.keys():
                res.update({'error': cmd_res.get('error')})
                self.send_message_error(res, ['post_process', 'total_process'])
                return res
            res.update({command: cmd_res})
        res.update({'instance_revert': self._need_revert})
        metrics = {'statuses': ['post_process', 'total_process'], 'stage': 'finished'}
        self.sender.send_result(res, 'Steps executed', metrics=metrics)
        self.done_trigger()
        return res

    def cloc_report(self):
        """This method generates a report by the cloc command the number of lines of code that has
        an instance and stores it in yaml format to be added as an attachment.

        :returns: a list of the dictionary that has the output of the cloc command in yaml format
            to be added as an attachment.
        :rtype: dict
        """
        res = {'command': 'cloc_report', 'attachments': list()}
        command_exists = self.__instance_manager.exec_cmd("which cloc")
        if not command_exists:
            res.update({
                'result': 'CLOC is not installed in the container, report not generated'
            })
            return res
        odoo_home = self.__instance_manager.\
            config.get('env_vars').get('odoo_home')
        module = os.path.join(odoo_home, 'instance')
        command_cloc = "cloc --yaml {module}".format(module=module)
        execute_cloc = self.__instance_manager.exec_cmd(command_cloc)
        body_content = execute_cloc.split('\n---')
        res.get('attachments').append(
            {
                "file_name": "cloc_report",
                "file": utils.decode(base64.b64encode(utils.encode(json.dumps(
                    yaml.load(body_content[1]), indent=4
                )))),
                "type": 'application/json'
            }
        )
        res.update({'result': 'CLOC report successfully generated'})
        return res

    def odoo_cloc_report(self):
        """This method generates a report by the cloc command the number of lines of code that has
        an instance and stores it in yaml format to be added as an attachment.

        :returns: a list of the dictionary that has the output of the cloc command in yaml format
            to be added as an attachment.
        :rtype: dict
        """
        res = {'command': 'odoo_cloc_report'}
        odoo_home = self.__instance_manager.config.get('env_vars').get('odoo_home')
        odoo_bin = '%(home)s/instance/odoo/%(bin)s' % {
            'bin': self.__instance_manager.odoo_binary, 'home': odoo_home}
        cmd = "%s cloc --help" % (odoo_bin)
        result = self.__instance_manager.exec_cmd(cmd)
        if 'Unknow command' in result:
            res.update({'result': 'The odoo-bin version does not have cloc command.'})
            return res
        logger.info("Starting generating odoo cloc report")
        odoo_conf = self.__instance_manager.config.get('env_vars').get('odoo_config_file')
        dbname = self.__config.instance_config.get('config').get('db_name')
        command_cloc = "%(bin)s cloc -d %(dbname)s -c %(conf)s" % {
            'bin': odoo_bin, 'dbname': dbname, 'conf': odoo_conf}
        result = self.__instance_manager.exec_cmd(command_cloc)
        headers = []
        odoo_cloc = {}
        if "Errors" in result:
            result, errors = result.split('Errors')
            res.update({'errors': errors})
        lines = result.split('\n')
        for line in lines:
            if headers and line.count('-') <= 5:
                values = [value for value in line.strip().split(" ") if value]
                if not values:
                    continue
                if len(values) == 3:
                    values_dict = {}
                    number = 0
                    for header in headers:
                        values_dict.update({header: values[number]})
                        number += 1
                    odoo_cloc.update({"total": values_dict})
                    continue
                values_dict = {}
                number = 0
                for header in headers:
                    number += 1
                    values_dict.update({header: values[number]})
                odoo_cloc.update({values[0]: values_dict})
            if "Odoo cloc" in line:
                line = line.replace("Odoo cloc", "")
                headers = [h for h in line.strip().split(" ") if h]
        res.update({'result': 'CLOC Odoo report successfully generated', 'odoo_cloc': odoo_cloc})
        logger.info("CLOC Odoo report successfully generated")
        return res

    def list_packages(self):
        """This method dumps a list of packages installed inside the container with `apt` and `pip`.
        """
        res = {
            'command': 'list_packages',
            'packages': self.__instance_manager.get_container_packages()
        }
        return res

    @events
    def restore(self):
        """Restores a backup from a file or folder. If a folder is provided, searches the best
        match for the given configuration. Database name is an optional parameter.

        The return value is a dict as follows::

            {
                'command': 'command executed',
                'result':
                {
                    'backup': 'backup file used to restore the database',
                    'database_name': 'the database name created with the corresponding backup'
                }
            }

        In case of any error::

            {
                'command': 'command executed',
                'error': 'error message'
            }

        :param backup_src: Backup source, can be a folder or a backup file.
        :type backup_src: str
        :param database_name: Database name to restore. If None, is generated automatically.
        :type database_name: str
        :param deactivate: Force db deactivation ignoring the instance type.
        :type deactivate: bool
        :returns: A json object with the result or error generated. If any result is generated the
            result key will have the backup used and the database name.
        :rtype: dict
        """
        metrics = {'statuses': ['restore'], 'stage': 'started'}
        self.sender.send_result(log='Creating database', metrics=metrics)
        self.__config.check_config('restore')
        res = {'command': 'restore', 'result': {}}
        database_name = self.__config.instance_config.get('config').get('db_name')
        restore_from = self.__config.instance_config.get('restore_db_from')
        if restore_from:
            msg = 'Copying database from: {}.'.format(restore_from.get('container_name'))
            self.sender.send_result(log=msg)
            logger.info(msg)
            commandv = CommandV({'container_config': {
                'container_name': restore_from.get('container_name'),
            }})
            backup_res = commandv.backup(False, restore_from.get('db_name'), cformat=False)
            if backup_res.get('error'):
                res.update({'error': backup_res.get('error')})
                self.send_message_error(res, ['restore', 'total_process'])
                return res
            self.__config.backup_src = backup_res.get('result').get('tmp_dir')
        if not self.__config.backup_src:
            result = self.create_db_demo()
            res.update(result)
            metrics.update({'stage': 'finished'})
            self.sender.send_result(res, metrics=metrics)
            self.restore_done_trigger()
            return res
        try:
            self.sender.send_result(log='Restoring a backup in the database "%s".' % (
                database_name))
            restore_res = self.__instance_manager.restore_database(
                database_name, self.__config.backup_src)
            res.update(restore_res)
        except (OperationalError, EOFError, AttributeError) as error:
            logger.exception(error)
            res.update({'error': utils.get_error_message(error)})
        if res.get('error', False):
            self.send_message_error(res, ['restore', 'total_process'])
            return res
        # Wait start the Odoo after deactivate the isntance unless it is a `production` type.
        if (self.__instance_manager.docker_id and
                self.instance_manager.instance_type == 'production'):
            self.__instance_manager.start_instance()
        logger.debug('restore_res: %s', str(restore_res))
        if restore_from and not self.__instance_manager.docker_id:
            utils.clean_files(self.__config.backup_src)
        user = self.instance_manager.get_odoo_users(database_name,
                                                    user_id=self.get_admin_id())
        res.get('result').update({'user_admin': (user and user[0] or {}).get("login")})
        params = {'database.generated_at': restore_res["result"].get('create_date'),
                  'database.type': self.instance_manager.instance_type}
        self.instance_manager.set_parameters(database_name, params)
        metrics.update({'stage': 'finished'})
        self.sender.send_result(res, log='Database "%s" created.' % (database_name),
                                metrics=metrics)
        self.restore_done_trigger()
        return res

    def _make_socket_request(self, driver, endpoint, method):
        """Performs a request to a DeployV socket that can handle btrfs/zfs backups.

        :param driver: Driver that should handle the requests, this can be `btrfs` or `zfs`.
        :param endpoint: Controller endpoint for the request, this can be `restore` or `backup`.
        :param method: Method that will be used for the request to the endpoint,
                       e.g. post, delete, get, etc.

        :return: Request object with the result of the request.
        """
        cfg = self.__config
        restore_type = ""
        if cfg.container_config.get('keep_db'):
            restore_type = 'W_KEEPDB'
        elif cfg.no_fs:
            restore_type = 'WO_FILESTORE'
        data = {
            "customer_id": cfg.instance_config.get("customer_id"),
            "task_id": cfg.instance_config.get("task_id"),
            "psql_version": self.instance_manager.get_postgres_version(),
            "db_name": cfg.instance_config.get('config').get('db_name'),
            "db_user": cfg.instance_config.get("config").get("db_user"),
            "db_export_port": str(cfg.instance_config.get('config').get('db_export_port', "")),
            "current_db_name": cfg.current_db_name,
            "current_db_user": cfg.current_db_user,
            "backup_type": cfg.backup_type,
            "type": restore_type,
            "backup_path": cfg.backup_src or os.getcwd(),
            "db_password": cfg.instance_config.get("config").get("db_password"),
            "instance_name": cfg.instance_config.get("config").get("container_name"),
            "psql_image": cfg.psql_image or "",
            "driver": driver
        }
        headers = {"Content-Type": "application/json"}
        url = ("http+unix://%2Fvar%2Frun%2Fdeployv%2Fdeployv.sock/{endpoint}"
               .format(endpoint=endpoint))
        session = requests_unixsocket.Session()
        if not hasattr(session, method):
            logger.error('The %s object has no attribute %s', type(session), method)
        func = getattr(session, method)
        res = func(url, headers=headers, json=data)
        return res

    @events
    def restore_snapshot(self):
        """Creates a new database based on a snapshot taken with btrfs or zfs.
        """
        metrics = {'statuses': ['restore'], 'stage': 'started'}
        self.sender.send_result(log='Creating database', metrics=metrics)
        self.__config.check_config('restore')
        res = {'command': 'restore', 'result': {}}
        database_name = self.__config.instance_config.get('config').get('db_name')
        self.__config.instance_config.get('config').update({'db_port': 5432})
        self.sender.send_result(log='Restoring a backup in the database "%s".' % database_name)
        request_res = self._make_socket_request(self.__config.backup_type,
                                                'restore', 'post').json()
        if request_res.get('code') and request_res.get('code') != 200:
            res.update(request_res)
            self.send_message_error(res, ['restore', 'total_process'])
            return res
        res.get('result').update(request_res)
        logger.debug('restore_res: %s', str(res))
        # The zfs socket does not return the abs path of the filestore.
        if not os.path.isabs(res['result'].get('filestore_path')):
            res['result'].update({'filestore_path': '/' + res['result'].get('filestore_path')})
        volumes = {
            res['result'].get('filestore_path'): {
                'bind': self.__config.container_config.get('volumes').get('filestore'),
                'ro': False
                }
        }
        postgres_container = self.instance_manager.config.get('postgres_container_name')
        postgres_info = self.instance_manager.inspect(postgres_container)
        db_host = postgres_info.get('NetworkSettings').get('Gateway')
        db_port = self.instance_manager.get_db_port(postgres_info)
        self.instance_manager.config.get('env_vars').update({
            'db_host': db_host, 'db_port': db_port, 'external_db_port': db_port})
        self.instance_manager._InstanceV__full_config.instance_config.get('config').update({
            'db_host': db_host, 'db_port': db_port})
        self.__config.container_config.get('volumes').update({
            'filestore': '{fs_path}:{vol}'.format(
                fs_path=res['result'].get('filestore_path'),
                vol=self.__config.container_config.get('volumes').get('filestore'))})
        db_config = self.__config.instance_config.get('config').copy()
        db_config.update({'db_port': db_port, 'db_host': db_host})
        user = self.instance_manager.get_odoo_users(database_name,
                                                    user_id=self.get_admin_id())
        res.get('result').update({'user_admin': (user and user[0] or {}).get("login")})
        params = {'database.generated_at': res["result"].get('create_date'),
                  'database.type': self.instance_manager.instance_type}
        self.instance_manager.set_parameters(database_name, params)
        self.new_deactivate(db_config)
        bash_lines = ["chown -R odoo:odoo /home/odoo/.local"]
        cmd_res = self.instance_manager.execute_in_auxiliary_container(database_name,
                                                                       bash_lines, volumes)
        if cmd_res.get('error'):
            res.update(cmd_res)
            self.send_message_error(res, ['restore', 'total_process'])
            return res
        metrics.update({'stage': 'finished'})
        self.sender.send_result(res, 'Database "%s" created.' % (database_name), metrics=metrics)
        self.restore_done_trigger()
        return res

    def _attach_file(self, msg, file_name, file_type):
        res = msg
        if not res.get('attachments', False):
            res.update({'attachments': list()})
        res.get('attachments').append(
            {
                'file_name': os.path.basename(file_name),
                'file': utils.generate_attachment(file_name),
                'type': file_type
            }
        )
        return res

    def _install_module(self, db_name):
        install_res = self.__instance_manager.install_module(
            self.__config.instance_config.get('install_module'),
            db_name
        )
        return install_res

    @events
    def backup(self):
        res = {'command': 'backup'}
        self.__config.check_config('backup')
        database_name = self.__config.instance_config.get('config').get('db_name')
        bkp_dir = self.__config.backup_src or os.getcwd()
        try:
            bkp = self.__instance_manager.generate_backup(
                {'db_name': database_name, 'dest_folder': bkp_dir})
        except errors.DumpError as error:
            logger.exception('Backup could not be generated')
            res.update({'error': 'Could not generate the backup: {0}'
                       .format(utils.get_error_message(error))})
            self.send_message_error(res)
            return res
        if bkp:
            res.update({'result': bkp})
            logger.info("Backup generated: %s", bkp)
        else:
            res.update({'error': 'Could not generate the backup'})
            logger.error(res['error'])
        self.sender.send_result(res)
        self.done_trigger()
        return res

    def deactivate_backup(self):
        self.__config.check_config('deactivate_backup')
        db_config = self.instance_manager.db_config
        db_helper_class = database_helper.DatabaseHelper.get_helper(use_template=False)
        extensions = self.__config.postgres.get('extensions')
        if (self.__config.instance_config.get('customer_id')
                in self.__config.postgres.get('avoid_postgis', [])):
            try:
                extensions.remove('postgis')
            except ValueError:
                pass
            try:
                extensions.remove('postgis_topology')
            except ValueError:
                pass
        db_helper = db_helper_class(
            utils.odoo2postgres(db_config), self.instance_manager._get_admin_config(),
            extensions)
        candidate = db_helper.search_candidate(self.__config.backup_src, self.__config.prefix)
        prefix = '{prefix}_deactivated'.format(prefix=self.__config.prefix)
        db_name = utils.generate_dbname({}, candidate[1], prefix)
        db_config.update({'db_name': db_name})
        self.__config.postgres.update({"deactivated_db_name": db_name})
        postgres = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        logger.info('Restoring backup to be deactivated')
        postgres.drop(db_name)
        try:
            dest_dir = utils.decompress_files(candidate[1], self.__config.temp_working_folder)
        except (EOFError, IOError) as error:
            error_msg = utils.get_error_message(error)
            logger.error(error_msg)
            return False
        restore_res = db_helper.create_database(
            dest_dir, db_name, db_config.get('db_user'), db_config.get('db_password'),
            jobs=self.__config.jobs)
        if not restore_res[0]:
            logger.error(restore_res[1])
            return False
        logger.info('Deactivating database')
        deactivate_res = self.instance_manager.deactivate_database(db_name)
        if deactivate_res.get('error'):
            self.send_message_error(deactivate_res)
            return deactivate_res
        admin_id = self.get_admin_id(db_config=db_config)
        instancev.InstanceV.change_password(admin_id, db_config.get('admin'), db_name, db_config)
        dump_path = 'dump.sql' if not self.__config.jobs else 'database_dump'
        dump_path = os.path.join(self.__config.temp_working_folder, dump_path)
        logger.info('Generating deactivated backup')
        exclude = self.__config.postgres.get("exclude_tables") or ""
        postgres.dump(db_name, dump_path, jobs=self.__config.jobs, exclude=exclude)
        backup_name = utils.generate_backup_name(db_name)
        files2backup = [dump_path]
        files = os.listdir(dest_dir)
        for element in files:
            if any([self.__config.no_fs and element == "filestore",
                    element in ['database_dump.sql', 'database_dump', 'dump.sql']]):
                continue
            full_path = os.path.join(dest_dir, element)
            files2backup.append(full_path)
        logger.info('Generating backup with the files %s', ', '.join(files2backup))
        if self.__config.cformat == "folder":
            backup = self.instance_manager._generate_decompressed_backup(
                files2backup, backup_name, self.__config.store_path)
        else:
            backup = utils.compress_files(
                backup_name, files2backup, dest_folder=self.__config.store_path,
                cformat=self.__config.cformat)
        postgres.drop(db_name, True)
        if self.__config.upload:
            utils.upload_file(backup, self.__config.upload)
            logger.info('File uploded to %s', self.__config.upload)
        if self.__config.remove:
            os.remove(backup)
        logger.info('Deactivated backup generated: %s', backup)
        self.done_trigger()
        return backup

    def change_passwords(self):
        """Generates a random password for each one of the users in an instance.
        """
        res = {'command': 'change_passwords'}
        results = {}
        db_name = self.instance_manager.db_config.get('db_name')
        self.sender.send_result(log='Changing passwords of the database "%s"' % (db_name))
        try:
            users = self.instance_manager.get_odoo_users(db_name)
        except OperationalError as error:
            error_msg = ("Failed to change the users passwords: {0}"
                         .format(error.message))
            res.update({'error': error_msg})
            self.send_message_error(res)
            return res
        admin_id = self.get_admin_id()
        admin_passwd = self.instance_manager.db_config.get(
            'admin_passwd') or utils.random_string(30)
        for user in users:
            if user.get('login') not in ['public', 'portaltemplate']:
                password = admin_passwd if admin_id == user.get('id') else utils.random_string(10)
                result = instancev.InstanceV.change_password(
                    user.get('id'), password, db_name, self.instance_manager.db_config)
                if result.get('error'):
                    res.update(result)
                    self.send_message_error(res)
                    return res
                results.update({user.get('login'): password})
        res.update({'result': results})
        self.sender.send_result(res, log='Passwords changed')
        self.done_trigger()
        return res

    def get_db_data(self, db_name, stage):
        logger.info('Retrieving the %s data from the db %s', stage, db_name)
        try:
            translations = self.instance_manager.get_translations(db_name)
            menus = self.instance_manager.get_menus(db_name)
            views = self.instance_manager.get_views(db_name)
            fields = self.instance_manager.get_fields(db_name)
        except OperationalError as error:
            error = 'Failed to obtain the data from {db}: {err}'.format(
                err=error.message, db=db_name)
            logger.error(error)
            self.sender.send_result(log=error, log_type='ERROR')
            raise
        db_data = {
            'translations': translations,
            'menus': menus,
            'views': views,
            'fields': fields
        }
        json_name = '%s_%s.json' % (db_name, stage)
        json_path = os.path.join(self.instance_manager.temp_folder, json_name)
        res = json_helper.save_json(db_data, json_path, ensure_ascii=True)
        return res

    def compare_databases(self):
        res = {'command': 'compare_databases'}
        self.sender.send_result(
            log='Comparing the data in the database from before and after the update'
        )
        db_name = self.__config.instance_config.get('config').get('db_name')
        tmp_path = self.instance_manager.temp_folder
        pre_update_data = json_helper.load_json_file(
            os.path.join(tmp_path, '%s_pre-update.json' % (db_name))
        ) or {}
        post_update_data = json_helper.load_json_file(
            os.path.join(tmp_path, '%s_post-update.json' % (db_name))
        ) or {}
        translations_diff = self.instance_manager.compare_translations(
            pre_update_data.get('translations'), post_update_data.get('translations'))
        menus_diff = self.instance_manager.compare_menus(
            pre_update_data.get('menus'), post_update_data.get('menus'))
        views_diff = self.instance_manager.compare_views(
            pre_update_data.get('views'), post_update_data.get('views'))
        fields_diff = self.instance_manager.compare_fields(
            pre_update_data.get('fields'), post_update_data.get('fields'))
        res.update({'result': {'translations': translations_diff,
                               'menus': menus_diff,
                               'views': views_diff,
                               'fields': fields_diff}})
        self.sender.send_result(res, log='Data compared')
        return res

    @events
    def updatedb(self, db_name=False):
        """Updates an instance (branches and database) and returns the json with a summary of the
        operation.

        :param database_name: Database name to be updated.
        :type database_name: str
        :returns: The result from :meth:`deployv.instance.instancev.run_and_log`.
        :rtype: dict
        """
        metrics = {'statuses': ['update'], 'stage': 'started'}
        self.__config.check_config('updatedb')
        res = {'command': 'updatedb', 'must_parse': True}
        db_name = db_name or self.__config.instance_config.get('config').get('db_name')
        if (self.__config.instance_config.get('instance_type') == 'updates' and
                self.__config.instance_config.get('auto_compare')):
            self.get_db_data(db_name, 'pre-update')
        self.sender.send_result(log='Updating database "%s"' % (db_name), metrics=metrics)
        try:
            self.__instance_manager.stop_instance()
        except APIError as error:
            error_msg = utils.get_error_message(error)
            logger.exception('Could not update database %s: %s', db_name, error_msg)
            res.update({'error': error_msg})
            self.send_message_error(res, ['update', 'total_process'])
            return res
        update_res = self.instance_manager.update_db(db_name)
        res.update(update_res)
        if res.get('error'):
            logger.error(res['error'])
        self.__instance_manager.start_instance()
        res['result'].update({'database_name': db_name})
        install_module = self.__config.instance_config.get('install_module')
        if install_module and not res.get('error'):
            self.sender.send_result(log='Installing module(s): %s' % (', '.join(install_module)))
            install_res = self.__instance_manager.install_module(install_module, db_name)
            res['result'].update({'install_module': install_res})
            if not res.get('attachments', False):
                res.update({'attachments': []})
            res.get('attachments').append({
                'file_name': os.path.basename(install_res.get('log_file')),
                'file': utils.generate_attachment(install_res.get('log_file')),
                'type': 'text/plain'
            })
        if not self.skip_push():
            image = self.__config.container_config.get('image_name')
            expr = r'(?P<url>[^/]*)/(?P<repo>.*):(?P<tag>.*)'
            match = re.match(expr, image)
            if not match:
                res.update({'error': ("Unable to push the updated image: Bad format in"
                                      " image name {img}").format(img=image)})
                self.send_message_error(res, ['update', 'total_process'])
                return res
            res.get('result').update({'image': image})
            tag = match.groupdict().get('tag')
            instance_type = self.__config.instance_config.get('instance_type')
            self.__config.container_config.get('push_image').append({
                'tag': tag,
                'base': self.instance_manager.config_variables.get('docker_image_repo')
                or self.__config.container_config.get('customer_image'),
                'tag_latest': bool(instance_type == 'updates')})
        if (self.__config.instance_config.get('instance_type') == 'updates' and
                self.__config.instance_config.get('auto_compare')):
            self.get_db_data(db_name, 'post-update')
        self._update_done = True
        metrics.update({'stage': 'finished'})
        self.sender.send_result(res, 'Database "%s" updated' % (db_name), metrics=metrics)
        self.update_done_trigger()
        return res

    def _stop_instance(self):
        try:
            self.__instance_manager.stop_instance()
        except (errors.CommandError, NotFound) as error:
            logger.debug('Error message %s', utils.get_error_message(error))
            utils.get_error_message(error)
            return 'Instance already deleted'
        except NullResource as error:
            error_msg = utils.get_error_message(error)
            if "image or container param is undefined" in error_msg:
                return 'Instance already deleted or misspelled name'
        return True

    def _drop_dbs(self, dbs_to_delete):
        db_config = self.instance_manager.db_config
        psql_dict = utils.odoo2postgres(db_config)
        psql_dict.update({"owner": db_config.get('db_owner'),
                          "owner_password": db_config.get('db_owner_passwd')})
        error_msgs = ["Connection refused", "password authentication failed"]
        try:
            psql_shell = postgresv.PostgresShell(psql_dict)
        except OperationalError as error:
            if any([msg in error.message for msg in error_msgs]):
                return
            raise
        res = []
        for db_name in dbs_to_delete:
            logger.debug('Dropping %s database', db_name)
            psql_shell.drop(db_name, force=True)
            res.append('Dropped %s database' % db_name)
        return res

    @events
    def delete_instance(self):
        """Delete an instance and database from the node.  If it does not exists or was already
        deleted, will indicate it in the message.

        :returns: A json object with the result or error generated. The result key will contain the
            generated result message, if any.
        :rtype: dict
        """
        config = self.instance_manager.config
        self.sender.send_result(log='Deleting container(s)')
        logger.info('Deleting container(s)')
        res = {'command': 'delete_instance'}
        result = []
        try:
            self.instance_manager.clean_volumes()
            if config.get('postgres_container_name') and not config.get('keep_db'):
                self.instance_manager.clean_volumes(config.get('postgres_container_name'))
        except (NullResource, errors.NotRunning, errors.CommandError) as error:
            allowed_errors = ['image or container param is undefined', 'is not running',
                              'Container does not exist']
            error_msg = utils.get_error_message(error)
            if any([allowed_error in error_msg for allowed_error in allowed_errors]):
                logger.error(
                    'Could not clean the container\'s volumes, container not found or not running'
                )
            else:
                res.update({'error': utils.get_error_message(error)})
                self.send_message_error(res)
                return res
        try:
            self.instance_manager.remove_container(config.get('container_name'))
            result.append('Instance {} deleted'.format(config.get('container_name')))
            if config.get('postgres_container_name') and not config.get('keep_db'):
                self.instance_manager.remove_container(config.get('postgres_container_name'))
                result.append('Instance {} deleted'.format(config.get('postgres_container_name')))
            if self.__instance_manager.instance_type == "develop":
                remove_img = self.instance_manager.remove_image(config.get('image_name'))
                result += remove_img
            if not config.get('keep_db'):
                res_dropdb = self.delete_database()
                result.extend(res_dropdb)
            res.update({
                'result': result
            })
            if self.__config.deployer.get('use_nginx'):
                self.update_nginx()
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.exception('Could not remove container')
            if "No such container or id: None" in utils.get_error_message(error):
                res.update({'result': 'Instance already deleted or misspelled name'})
            else:
                res.update({'error': utils.get_error_message(error)})
            self.send_message_error(res)
            return res
        self.sender.send_result(res, 'Container(s) deleted')
        self.destroy_done_trigger()
        return res

    def delete_database(self):
        """Method used to check if the database should be deleted by this worker
        using `DROP DATABASE` or if it should be requested to a btrfs/zfs driver.
        """
        db_name = self.__config.instance_config.get('config').get('db_name')
        if not self.use_btrfs() and not self.use_zfs():
            res_dropdb = self._drop_dbs([db_name])
            return res_dropdb
        request_res = self._make_socket_request(self.__config.backup_type,
                                                'restore', 'delete').json()
        if request_res.get('code') and request_res.get('code') != 200:
            raise errors.CommandError(
                'delete', 'Failed to remove the database: %s' % request_res.get('error'))
        res = ['Dropped %s database' % db_name]
        return res

    def get_containers(self):
        """Gets the containers list that are currently executing, which names match the
        regex: '^/([tiu][0-9]+_[a-z]+[0-9]+)_odoo', for example: 't111_cust80_odoo'.

        :return: Containers (as dict) with the domain and mapping ports.
        :rtype: list
        """
        cli = from_env().api
        containers = cli.containers()
        res = list()
        logger.debug('Geting containes names')
        regex = r'/([\w\d\_\-\.]+)_odoo$'
        for container_info in containers:
            for name in container_info.get('Names'):
                logger.debug('Name : %s', name)
                domain = re.match(regex, name)
                if not domain:
                    continue
                domain = domain.group(1).replace('_', '-')
                inspected = self.instance_manager.inspect(container_info.get('Id'))
                envs = inspected.get('Config').get('Env')
                envs = container.parse_env_vars(envs)
                if envs.get('instance_type') != 'develop':
                    continue
                ports_info = container.get_ports_dict(inspected)
                web_port = ports_info.get('8069')
                longpolling_port = ports_info.get('8072')
                # If the port was not exposed to all interfaces, it will be a
                # list with the IPs where it was exposed. We only need the port
                if isinstance(web_port, list):
                    web_port = web_port[0].split(":")[1]
                if isinstance(longpolling_port, list):
                    longpolling_port = longpolling_port[0].split(":")[1]
                res.append({
                    'domain': domain,
                    'port': web_port,
                    'lp_port': longpolling_port,
                    'logs': os.path.join(
                            os.path.expanduser(
                                    self.__config.container_config.get('working_folder')
                            ),
                            inspected.get('Name')[1:])
                })
                break
        return res

    @events
    def update_nginx(self):
        """Updates nginx config file to match running containers. If any are stopped or removed,
        they will be removed from nginx config.

        :return: Containers config. See :meth:`deployv.base.commandv.get_containers`.
        :rtype: dict
        """
        containers_config = self.get_containers()
        nginx_manager = nginxv.NginxV(self.__config)
        nginx_manager.update_sites(containers_config)
        nginx_manager.restart()
        return containers_config

    @events
    def push_image(self):
        res = {
            'command': 'push_image',
            'result': {},
            'attachments': [],
        }
        if self.skip_push():
            self.push_images_done_trigger()
            return res
        manager = self.__instance_manager
        images = self.__config.container_config.get('push_image')
        self.sender.send_result(log='Pushing images')
        if not images:
            res.update({
                'error': ("No images to updload were specified. Please specify"
                          " at least one in container_config > push_image")})
            self.send_message_error(res)
            return res
        pushed_imgs = []
        for img in images:
            local_image = img.get('image') or pushed_imgs and pushed_imgs[-1]
            if not local_image:
                push_result = manager.commit_and_push(img.get('base'), img.get('tag'))
            else:
                push_result = manager.tag_and_push(local_image, img.get('base'), img.get('tag'))
            if push_result.get('error'):
                res.update({'error': push_result.get('error')})
                self.send_message_error(res)
                return res
            push_details = push_result.get('result').get('push_result').get('log')
            res.get('attachments').append({
                'file_name': 'push_image_{tag}.json'.format(tag=img.get('tag')),
                'file': base64.b64encode(utils.encode(json.dumps(push_details, indent=4))),
                'type': 'application/json',
            })
            instance_type = self.__config.instance_config.get('instance_type')
            pushed_imgs.append({'name': push_result.get('result').get('tagged_image'),
                                'tag_latest': img.get('tag_latest'),
                                'tag_dev': bool(instance_type == 'develop')})
        res['result'].update({'images': pushed_imgs})
        self.sender.send_result(res, 'Images pushed')
        self.push_images_done_trigger()
        return res

    def create_db_demo(self):
        """ This method creates an empty database.

        :return: The name of the database
        :rtype: str
        """
        res = {'result': {}}
        self.sender.send_result(log='Creating a clean database')
        self._stop_instance()
        db_name = self.instance_manager.db_config.get('db_name')
        self._drop_dbs([db_name])
        db_name = db_name or utils.generate_dbname(self.__config, False, self.__config.prefix)
        postgres = postgresv.PostgresShell(utils.odoo2postgres(self.instance_manager.db_config))
        postgres.create(db_name)
        postgres_admin = postgresv.PostgresShell(self.instance_manager._get_admin_config())
        for extension in self.__config.postgres.get('extensions'):
            if (self.__config.postgres.get('customer_id')
                    in self.__config.postgres.get('avoid_postgis', [])
                    and extension in ['postgis', 'postgis_topology']):
                continue
            postgres_admin.create_extension(db_name, extension)
        self.instance_manager.create_extension_unaccent(db_name)
        create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.instance_manager.update_db(db_name, ['all'])
        res.get('result').update({'database_name': db_name, 'create_date': create_date})
        params = {'database.generated_at': create_date,
                  'database.type': self.instance_manager.instance_type}
        self.instance_manager.set_parameters(db_name, params)
        self.sender.send_result(log='Database "%s" created' % (db_name))
        return res

    def _check_free_space(self):
        """ Checks if there is enough free space in the paths where the compressed and the
        decompressed backups will be stored.

        :return: dictionary with the `error` key if an error ocurred or empty if there is
        enough space
        :rtype: dict
        """
        res = {}
        decompressed = utils.parse_backup_size(self.__config.decompressed_backup_size)
        compressed = utils.parse_backup_size(self.__config.compressed_backup_size)
        if decompressed['size_unit'] != compressed['size_unit']:
            converted_compressed = utils.byte_converter(self.__config.compressed_backup_size,
                                                        to_unit=decompressed['size_unit'])
            compressed = utils.parse_backup_size(converted_compressed)
        if (self.__config.temp_folder == self.__config.backup_src or
                self.__config.backup_src in self.__config.temp_folder):
            expected_size_value = compressed['size_value'] + decompressed['size_value']
            if self.__config.cformat == 'folder':
                expected_size_value = decompressed['size_value']
            expected_size = '{value}{unit}'.format(value=expected_size_value,
                                                   unit=decompressed['size_unit'])
            if not utils.verify_free_disk_space(expected_size, self.__config.backup_src):
                res.update({'error': 'Not enough disk space available in {directory}.'.format(
                    directory=self.__config.backup_src)})
            return res
        if not utils.verify_free_disk_space(self.__config.decompressed_backup_size,
                                            self.__config.temp_folder):
            res.update({'error': 'Not enough disk space available in {directory}.'.format(
                directory=self.__config.temp_folder)})
        elif not utils.verify_free_disk_space(self.__config.compressed_backup_size,
                                              self.__config.backup_src):
            res.update({'error': 'Not enough disk space available in {directory}.'.format(
                directory=self.__config.backup_src)})
        return res

    def _check_update_production_requirements(self):
        res = {'command': 'update_production', 'result': {}, 'must_parse': True}
        # Check images
        images_data = [
            {
                'image_name': self.__config.container_config.get('image_name'),
                'image_size': self.__config.image_size
            }
        ]
        if self.__config.maintenance_page:
            images_data.append(self.__config.maintenance_page)
        images_path = utils.get_images_path()
        logger.info('Cheking disk space required for the images')
        for image in images_data:
            name = image.get('image_name')
            if not image.get('image_size'):
                logger.warning(
                    'No expected image size was provided for the image %s,'
                    ' skipping this check', name)
            elif not utils.verify_free_disk_space(image.get('image_size'), images_path):
                msg = ('There is not enough space in disk for the image {image_name}.'
                       ' Required space: {image_size}'.format(**image))
                res.update({'error': msg})
                self.sender.send_result(res, msg, 'ERROR')
                return False
            logger.info('Pulling image "%s"', name)
            self.sender.send_result(log='Pulling image %s' % (name))
            try:
                self.instance_manager.pull(name, True)
            except (errors.NoSuchImage, APIError, ImageNotFound):
                msg = 'Image "{img}" doesn\'t exist'.format(img=name)
                res.update({'error': msg})
                self.sender.send_result(res, msg, 'ERROR')
                return False
        # Check postgres config
        with postgresv.PostgresConnector(
                utils.odoo2postgres(self.instance_manager.db_config)) as conn:
            db_conn = conn.check_config()
        if not db_conn:
            msg = 'Failed to connect to the database'
            res.update({'error': msg})
            self.sender.send_result(res, msg, 'ERROR')
            return False
        logger.debug('Postgres config check successful')
        # Check free space
        free_space = self._check_free_space()
        if free_space.get('error'):
            res.update({'error': free_space.get('error')})
            self.sender.send_result(res, free_space['error'], 'ERROR')
            return False
        logger.debug('Space check successful')
        # Check working folder
        working_folder = self.instance_manager.config.get("working_folder")
        if not os.path.isdir(os.path.expanduser(working_folder)):
            msg = 'The {folder} working folder does not exist.'.format(folder=working_folder)
            res.update({'error': msg})
            self.sender.send_result(res, msg, 'ERROR')
            return False
        logger.debug('Working folder check successful')
        return True

    def update_production(self):
        """Updates a production instance.

        The process is as follows:

            1. The free disk space is checked to see if there is enough to generate the backups.
            2. The production container is committed as the stable one, and pushed to the repo.
            3. The backup is generated (but not compressed).
            4. The current production container is destroyed.
            5. The modules are updated in the database using the updates image.
            6. The new production container is started.
            7. The backup is compressed inside the backup folder.
        """
        metrics = {'statuses': ['total_process', 'total_pre_process', 'database_backup'],
                   'stage': 'started'}
        self.sender.send_result(log='Updating Production instance', metrics=metrics)
        res = {'command': 'update_production', 'result': {}, 'must_parse': True}
        self.__config.check_config('update_production')
        container_info = self.instance_manager.basic_info
        container_name = container_info.get('name')
        branches_json = os.path.join(self.instance_manager.temp_folder, 'repositories.json')
        manifest_path = self.instance_manager._get_db_manifest(self.__config.temp_working_folder)
        data_dir = self.instance_manager.get_data_dir()
        switch_res = self._switch_production_container(container_name)
        if switch_res.get('error'):
            res.update({'error': switch_res.get('error')})
            self.send_message_error(res, ['total_process'])
            return res
        prefix = self.__config.instance_config.get('customer_id') or self.__config.prefix
        backup_params = {'additional_files': [branches_json, manifest_path],
                         'prefix': prefix, 'data_dir': data_dir}
        backup_result = self._production_backup(container_name, backup_params)
        metrics = {'statuses': ['database_backup'], 'stage': 'finished'}
        self.sender.send_result(metrics=metrics)
        logger.debug('Backup result: %s', json.dumps(backup_result, indent=2))
        start_result = self._production_update_and_start(container_name, switch_res.get('result'))
        if start_result.get('error'):
            res.update(start_result)
            self.__config.container_config.update({'image_name': self.__config.previous_image})
            self._need_revert = True
            self.send_message_error(res, ['total_process', 'total_pre_process'])
            return res
        tag_result = self._production_commit_and_tag_stable()
        if tag_result.get('error'):
            res.update({'error': tag_result.get('error')})
            self.send_message_error(res, ['total_process', 'total_pre_process'])
            return res
        logger.debug('Commit and tag stable result: %s', json.dumps(tag_result, indent=2))
        stable_image = tag_result.get('result').get('stable_image')
        res['result'].update({
            'stable_image': stable_image,
            'tagged_image': tag_result.get('result').get('tagged_image'),
            'modules': start_result.get('result').get('modules'),
            'update_logs': start_result.get('result').get('update_logs'),
            'result_type': 'pre-backup'
        })
        path_branches = self.instance_manager.save_repositories("repositories.json")
        start_result.get('attachments').append({
            'file_name': os.path.basename(path_branches),
            'file': utils.generate_attachment(path_branches),
            'type': 'application/json'
        })
        res.update({'attachments': start_result.get('attachments')})
        logger.debug('Update and start result: %s', json.dumps(start_result, indent=2))
        full_res = res.copy()
        metrics = {'statuses': ['total_pre_process'], 'stage': 'finished'}
        self.sender.send_result(res, metrics=metrics)
        backup = backup_result.get('result').get('backup')
        compress_result = self._production_compress_backup(
            container_name, backup['files'], backup['name'],
            self.__config.backup_src or os.getcwd(), self.__config.cformat, backup['tmp_dir'])
        if compress_result.get('error'):
            res.update({'error': compress_result.get('error')})
            self.send_message_error(res, ['total_process'])
            return res
        logger.debug('Compress result: %s', json.dumps(compress_result, indent=2))
        odoo_cloc = self.odoo_cloc_report()
        self.sender.send_result(odoo_cloc)
        # Done
        backup_name = compress_result.get('result')
        logger.info('Production instance successfully updated')
        full_res['result'].update({
            'backup': backup_name,
            'backup_size': utils.get_size(backup_name),
            'result_type': 'post-backup'
        })
        full_res.update({'attachments': start_result.get('attachments')})
        metrics = {'statuses': ['total_process'], 'stage': 'finished'}
        self.sender.send_result(full_res, 'Production instance successfully updated',
                                metrics=metrics)
        self.done_trigger()
        return res

    def _production_commit_and_tag_stable(self):
        """Commits the production container as stable and with the current date, and
        pushes the generated images to the repository.

        (This method shouldn't be called directly, instead use: `update_production`.)
        """
        res = {'result': {}}
        # Commit container and push image
        manager = self.__instance_manager
        variables = manager.config_variables
        image_name = self.__config.container_config.get('image_name')
        image_repo = image_name.split(':')[0]
        base_tag_name = "%(app)s-%(version)s" % {
            "app": variables.get("main_app"), "version": variables.get("version")}
        date_tag = "%(base)s-%(date)s" % {
            "base": base_tag_name, "date": utils.get_strtime()}
        self.sender.send_result(log='Pushing image %s:%s' % (image_repo, date_tag))
        commit_result = manager.commit_and_push(image_repo, date_tag)
        if commit_result.get('error'):
            res.update({'error': commit_result.get('error')})
            return res
        # Tag updates as stable and push
        self.sender.send_result(log='Pushing scheduled image %s as stable' % (image_name))
        tag = "%(base)s-stable" % {"base": base_tag_name}
        tag_result = manager.tag_and_push(image_name, image_repo, tag=tag)
        if tag_result.get('error'):
            res.update({'error': tag_result.get('error')})
        res['result'].update({
            'container_info': commit_result.get('result').get('container_info'),
            'tagged_image': commit_result.get('result').get('tagged_image'),
            'updates_image': image_name,
            'stable_image': tag_result.get('result').get('tagged_image'),
        })
        return res

    def _production_backup(self, container_name, backup_params):
        """Backups the production instance and destroys its current container.

        (This method shouldn't be called directly, instead use: `update_production`.)

        :param container_name: The production container name.
        :param backup_params: dict with the params required to generate the backup
        """
        manager = self.instance_manager
        res = {'result': {}}
        # Dump backup
        db_name = self.__config.instance_config.get('config', {}).get('db_name')
        info_msg = 'Generating backup for "{}" with DB "{}"'.format(container_name, db_name)
        self.sender.send_result(log='Generating backup')
        logger.info(info_msg)
        self.__config.reason = self.__config.reason or 'preupdate'
        # Change the cformat to False in order to receive the dict of files only
        original_cformat = self.__config.cformat
        self.__config.cformat = False
        backup_params.update({'db_name': db_name, 'cformat': False,
                              'dest_folder': self.__config.backup_src})
        backup = manager.generate_backup(backup_params)
        # Revert the cformat to be used to compress the backup
        self.__config.cformat = original_cformat
        self.sender.send_result(log='Temporary backup generated in "%s"' % (backup))
        logger.info('Temporary backup generated in "%s"', backup)
        res['result'].update({'backup': backup})
        return res

    def _production_update_and_start(self, container_name, maintenance_container=False):
        """Updates the production database using the updates image and starts the new production
        container.

        (This method shouldn't be called directly, instead use: `update_production`.)

        :param container_name: The name for the production container.
            successfully started.
        :param maintenance_container: Name of the intermediate container that was
            deployed for the production downtime.

        :type container_name: str
        :type maintenance_container: str
        """
        modules = self.__config.instance_config.get('update_module')
        db_config = self.instance_manager.db_config
        msg = 'Updating modules "{mod}" in "{db}" using "{img}""'.format(
            mod=", ".join(modules), db=db_config.get('db_name'),
            img=self.__config.container_config.get('image_name'))
        metrics = {'statuses': ['update'], 'stage': 'started'}
        self.sender.send_result(log=msg, metrics=metrics)
        res = self.instance_manager.update_db(db_config.get('db_name'))
        # Remove maintenance container despite if the process finished successfully or not.
        if maintenance_container:
            self.instance_manager.remove_container(maintenance_container)
        if res.get('error'):
            return res
        # Create container
        self.sender.send_result(log='Starting instance')
        logger.info('Starting container and instance in "%s"', container_name)
        self.instance_manager.start_odoo_container()
        # Start instance
        logger.info('Waiting for Odoo to start in "%s"', container_name)
        started = self.instance_manager.ensure_instance_status(
            ensure_running=True, max_tries=self.__config.status_checks)
        if not started:
            res.update({'error': 'Instance not running in "{container}"'.format(
                container=container_name
            )})
            return res
        metrics.update({'stage': 'finished'})
        self.sender.send_result(log='Production instance started', metrics=metrics)
        res['result'].update({
            'modules': modules or [],
            'container_name': container_name,
        })
        return res

    def _production_compress_backup(self, container_name, files, name, directory, cformat, tmp):
        """Compresses the production backup.

        (This method shouldn't be called directly, instead use: `update_production`.)

        :param container_name: The container name.
        :param files: The files to be compressed.
        :param name: The name for the backup file.
        :param directory: Where the backup will be saved.
        :param cformat: The format for the backup.
        :param tmp: The temporal directory where the backup was generated.

        :type container_name: str
        :type files: list
        :type name: str
        :type directory: str
        :type cformat: str
        :type tmp: str
        """
        manager = self.__instance_manager
        res = {'result': {}}
        # Compress backup
        self.sender.send_result(log='Compressing production backup')
        logger.info('Compressing backup for "%s" in "%s"', container_name, directory)
        try:
            result_file = manager.return_backup(files, name, directory, cformat)
        except IOError as error:
            res.update({'error': 'Failed to generate backup: {err}'.format(err=str(error))})
            return res
        self.sender.send_result(log='Backup production generated')
        logger.info('Backup generated in "%s"', result_file)
        utils.clean_files(tmp)
        res.update({'result': result_file})
        return res

    def _switch_production_container(self, container_name):
        res = {'result': False}
        manager = self.instance_manager
        # Get the info of the repos
        self.__instance_manager.save_repositories("repositories.json")
        # Stop instance
        logger.info('Stopping instance in "%s"', container_name)
        self.sender.send_result(log='Stopping instance')
        stopped = manager.ensure_instance_status(
            ensure_running=False, max_tries=self.__config.status_checks
        )
        if not stopped:
            res.update({'error': 'Couldn\'t stop instance in "{container}"'.format(
                container=container_name
            )})
            return res
        # Terminate connections
        db_config = manager.db_config
        pg_shell = postgresv.PostgresShell(utils.odoo2postgres(db_config))
        pg_shell.terminate_sessions(db_config['db_name'], db_config.get('db_owner'),
                                    db_config.get('db_owner_passwd'))
        # remove tmp volume
        tmp_volume = manager.config.get('volumes').get('tmp')
        logger.info('Removing temp folder volume: %s', tmp_volume)
        manager.exec_cmd('rm -rf %s' % (tmp_volume))
        # Remove container
        logger.info('Removing container "%s"', container_name)
        manager.remove_container()
        # start maintenance page's container
        if self.__config.maintenance_page:
            maintenance_container_name = manager.start_maintenance_page_container()
            res.update({'result': maintenance_container_name})
        return res

    def restart_instance(self):
        """Restarts the odoo inside the container and checks if an error
        occurred or if it started successfully.
        """
        res = {'command': 'restart_instance'}
        self.sender.send_result(log='Restarting instance')
        restart_res = self.instance_manager.restart_instance()
        # Add anything returned by the restart_instance() method to the result key, despite
        # if it was an error or not, so orchest won't move the deploy to the error state
        res.update({'result': restart_res.get('result') or restart_res.get('error')})
        log_type = 'error' in restart_res.keys() and 'ERROR' or 'INFO'
        self.sender.send_result(res, res.get('result'), log_type)
        return res

    def restart_container(self):
        """Restarts the docker container and checks if it started properly
        """
        res = {'command': 'restart_container'}
        self.sender.send_result(log='Restarting container')
        restart_res = self.instance_manager.restart_container()
        results = {
            True: 'Instance successfully restarted',
            False: ('Failed to restart the container, it may be because it'
                    ' does not exist or it took too long to start')
        }
        res.update({'result': restart_res, 'msg': results.get(restart_res)})
        self.sender.send_result(res, res.get('msg'), restart_res and 'INFO' or 'ERROR')
        return res

    def get_utcnow(self):
        """Method that get the current utc date and convert it to string.
        :return: return the utc date in string.
        :rtype: str
        """
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    def send_message_error(self, res, metrics=False):
        """Send a message error with the data of `res` parameter and
        other message with the data of finished metric.
        :param res: the data that will send in the message.
        :type: dict
        :param status: The status of metric.
        :type: str
        """
        if metrics:
            metrics = {'statuses': metrics, 'stage': 'finished'}
        self.sender.send_result(res, res.get('error'), 'ERROR', metrics)
        self.error_trigger()

    def create_working_folder(self):
        """Create a folder that can use in any command executed.
        """
        if os.path.exists(self.__config.temp_working_folder or ''):
            return
        self.__config.working_folder = self.__config.working_folder or self.__config.temp_folder
        utils.makedir(self.__config.working_folder)
        self.__config.temp_working_folder = mkdtemp(
            prefix='deployv_', dir=self.__config.working_folder)

    def clean_working_folders(self):
        """Remove working forlder
        """
        utils.clean_files(self.__config.temp_working_folder)

    @events
    def verify_quantity_instances(self):
        """Verify that max limit of deployed instances won't be exceeding"""
        res = {'command': 'create', 'result': {}}
        container_name = self.__config.container_config.get('container_name')
        if not self._can_add_new(container_name):
            msg = 'Reached max instance count for this node ({} allowed)'.format(
                self.__config.deployer.get('max_instances'))
            logger.error(msg)
            res.update({'error': msg})
            self.send_message_error(res)
            raise Exception(msg)
        return {}

    def commit_history(self):
        """ Downloads the repositories if they do not exist, and if the do
        it pulls the latest changes, gets the different commits between two commits
        specified in the repos and ref_repos dictionary
        """
        msg = self.__config.commit_history
        res = {'command': 'commit_history', 'result': {}, 'build_id': msg.get('build_id')}
        name = msg.get('repo').get('name')
        manager = git_helper.GitManager(
            self.__config.temp_working_folder,
            self.__config.deployer.get('commit_history_folder'), msg.get('ssh_key'))
        logger.info('Generating commit history of %s.', name)
        history = manager.get_commit_history(msg.get('repo'), msg.get('ref'))
        res['result'] = history
        if history.get('error'):
            logger.error('Failed to generate the commit history of %s/%s: %s',
                         name, msg.get('repo').get('branch'), history.get('error'))
        else:
            logger.info('Generated the commit history of %s.', name)
        self.sender.send_result(res)
        self.done_trigger()

    def new_deactivate(self, config=False):
        old_db_config = self.instance_manager.db_config.copy()
        self.instance_manager.db_config.update(config)
        db_config = self.instance_manager.db_config
        database = db_config.get('db_name')
        self.sender.send_result(log='Deactivating database %s.' % (database))
        self.__config.check_config('deactivate')
        extra_config = {
            'nginx_url': self.instance_manager.config.get('nginx_url'),
            'use_mailhog': self.__config.instance_config.get("use_mailhog")}
        deactivate_res = self.instance_manager.deactivate_database(database, extra_config)
        if deactivate_res.get('error'):
            self.send_message_error(deactivate_res)
            return deactivate_res
        new_admin = db_config.get('admin', False)
        if new_admin:
            db_config.update({'db_name': database})
            admin_id = self.get_admin_id(db_config=db_config)
            instancev.InstanceV.change_password(admin_id, new_admin, database, db_config)
        self.sender.send_result(log='Database %s deactivated.' % (database))
        self.instance_manager.db_config.update(old_db_config)
