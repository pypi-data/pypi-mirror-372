import deployv_static
import logging
import simplejson as json
import spur
import re
import docker
import shutil
from docker import from_env
from deployv.helpers import utils
from deployv.base.errors import BuildError, NoItemFound
from deployv.instance import ODOO_BINARY
from os import path, getenv, makedirs


_logger = logging.getLogger(__name__)


class BuildImage:

    def __init__(self, config, variables):
        """ Helper that builds new docker images
            If the config has the full_stack equal True, it creates a new image
            with full stack tools, that is:
                - PostgreSQL
                - Nginx
                - Supervisor
                - Odoo
                - Openssh-server

            :param config: Config Config object with the format used by deployv.
        """
        self.client = from_env().api
        self._config = config
        self._config.tag = self._config.tag or self._generate_image_name()
        self._files_folder = path.join(self._config.temp_working_folder, 'files')
        self.instance_path = path.join(self._config.temp_working_folder, 'instance')
        self.variables = variables

    def _generate_image_name(self):
        """ Generates the name that the new image will have depending on the parameters
        used to build it, the name is created as follows:

        - Exactly one repo: { repo_name }{ repo_branch }
        - Zero or more than one repo: { task_id }_{ customer_id }_image
        - full_stack_image = True: { task_id }_full_odoo_stack
        """
        ins_cfg = self._config.instance_config
        main_repo = utils.get_main_repo(ins_cfg.get('repositories', []))
        name = '%s_%s_image' % (ins_cfg.get('task_id'), ins_cfg.get('customer_id'))
        if self._config.container_config.get('full_stack'):
            name = '%s_full_odoo_stack' % (ins_cfg.get('task_id'))
        elif main_repo:
            name = '%s%s' % (main_repo.get('name'), main_repo.get('branch'))
        return utils.clean_string(name)

    def _render_files(self):
        """Render the files that will use to build the image.
        """
        makedirs(self._files_folder)
        templates = [('config_lc_collate.jinja', 'config_lc_collate.sql'),
                     ('dev_instances.jinja', 'dev_services.conf'),
                     ('entrypoint_image.jinja', 'entrypoint_image'),
                     ('odoo_service.jinja', 'odoo_service.conf')]
        values = {
            'db_user': self._config.instance_config.get('config').get('db_user'),
            'db_password': self._config.instance_config.get('config').get('db_password'),
            'odoo_binaries': " ".join(["-e "+i for i in ODOO_BINARY.values()]),
            'odoo_binary': ODOO_BINARY[self.variables.get('version')],
            'psql_version': self.variables.get('psql_version'),
        }
        if self._config.container_config.get('build_image'):
            templates.append(('postgres_service.jinja', 'postgres_service.conf'))
        for template in templates:
            template_contents = utils.render_template(template[0], values)
            with open(path.join(self._files_folder, template[1]), 'w') as obj:
                obj.write(template_contents)
        # Copy all the files
        files = ['getaddons.py', 'install_deps.py',
                 'openerp_serverrc', 'supervisord_service.conf', 'get_release_data.py']
        for file_name in files:
            file_path = deployv_static.get_template_path(file_name)
            shutil.copy(file_path, self._files_folder)

    def _generate_apt_requirements(self):
        """ Creates a file called apt_dependencies.txt in the deployv/templates/files with all
        the apt dependencies specified in the apt_install parameter in the json, this file is used
        by the install_deps.py script to install those dependencies during the build
        """
        deps_path = path.join(self._files_folder, 'apt_dependencies.txt')
        apt_requirements = self._config.container_config.get('apt_install')
        with open(deps_path, 'w') as fileobj:
            for requirement in apt_requirements:
                fileobj.write(requirement + '\n')
        return deps_path

    def _create_image(self, template, values):
        """ Build a new image using a Dockerfile created by rendering a template with the
            parameters provided by the user.

            :param template: name of the template that will be used to create the dockerfile,
                             Dockerfile.jinja for the full stack image and base_dockerfile.jinja
                             for the image with the repos and their oca dependencies.
            :param values: values used to render the template

            :return: Name of the new image.
        """
        _logger.info('pulling base image %s', values.get('base_image_name'))
        res = False
        try:
            self.client.pull(values.get('base_image_name'))
        except docker.errors.NotFound:
            _logger.debug('Image not found in hub')
        docker_content = utils.render_template(template, values)
        with open(path.join(self._config.temp_working_folder, 'Dockerfile'), 'w') as docker_file:
            docker_file.write(docker_content)
        _logger.info('Building image')
        streams = []
        ansi_escape = re.compile(r'\x1b[^m]*m')
        for line in self.client.build(path=self._config.temp_working_folder, timeout=3600,
                                      rm=True, tag=self._config.tag):
            obj = utils.json_helper.load_json_string(line)
            if obj.get('stream'):
                # Keep a history of the streams. This is because sometimes the
                # messages get cut in the middle between streams.
                streams.append(obj.get('stream'))
                _logger.info(obj.get('stream').strip())
            elif obj.get('error'):
                _logger.error(obj.get('error').strip())
                # If we have a stream history, get the last five streamed messages.
                # This is to join any possible splitted message.
                if streams:
                    msg = "".join(streams[-5:])
                else:
                    # Else, just get the generic error message.
                    msg = obj.get('error')
                # Get only the last line from the error, because that's the
                # actual error message, and skip the traceback.
                msg = [val for val in ansi_escape.sub('', msg).split("\n") if val]
                raise BuildError(msg[len(msg)-1].strip())
        image_sha = self.client.images(name=self._config.tag, quiet=True)
        res = image_sha and utils.decode(image_sha[0]).split(':')[1][:10]
        return res

    def _apply_patches(self):
        """Searches for a file named `patches.txt` and applies the git patches
        specified in it directly in the specified repositories.
        """
        res = {'result': []}
        shell = spur.LocalShell()
        try:
            main_repo = self._config.get_mainrepo_path()
        except NoItemFound:
            _logger.error('Main repo not specified in the json config, skipping patches')
            return res
        patches_path = path.join(self.instance_path, main_repo, 'patches.txt')
        if not path.exists(patches_path):
            return res
        patches = utils.read_lines(patches_path)
        if not patches:
            return res
        _logger.info('Applying patches from %s', patches_path)
        headers = [
            '--header=Authorization: token %s' % getenv('GITHUB_TOKEN'),
            '--header=Accept: application/vnd.github.VERSION.patch'
        ]
        for patch in patches:
            patch_parts = patch.split(' ', 1)
            repo = patch_parts[0]
            url = patch_parts[1]
            file_path = path.join(self._config.temp_folder, 'deployv.patch')
            cmd = ['wget', url, '-O', file_path]
            if 'api.github.com' in url:
                _logger.debug('A patch from a private repo will be applied: %s', url)
                cmd += headers
            try:
                shell.run(cmd)
            except spur.results.RunProcessError as error_obj:
                error = ('An error occurred while downloading the patch %s:\n%s' %
                         (url, error_obj.stderr_output))
                _logger.error(error)
                return {'error': error}
            repo_path = path.join(self.instance_path, repo)
            try:
                shell.run(['patch', '-f', '-p1', '-i', file_path, '-d', repo_path])
            except spur.results.RunProcessError as error_obj:
                error = ('An error occurred while applying the patch %s' % url)
                _logger.error(error)
                _logger.error(error_obj.stderr_output)
                _logger.error(error_obj.output)
                return {'error': error}
            shell.run(['rm', file_path])
            res.get('result').append(url)
        return res

    def build(self):
        """ Main method that builds the new image using the information
            provided by the user.

            :return: Dictionary with the name of the new image
        """
        res = {}
        _logger.info('Building image')
        # Copies the files that will be used for the build
        try:
            self._render_files()
        except IOError as error:
            res.update({'error': utils.get_error_message(error)})
            return res
        image_name = self._config.container_config.get('image_name')
        db_config = self._config.instance_config.get('config')
        values = {'db_user': db_config.get('db_user'),
                  'db_password': db_config.get('db_password'),
                  'base_image_name': self.variables.get('base_image')}
        if self._config.container_config.get('build_image'):
            self._generate_apt_requirements()
            patches_res = self._apply_patches()
            if patches_res.get('error'):
                return patches_res
            _logger.info('Patches applied:\n %s', '\n'.join(patches_res.get('result')))
            values.update({'variables': self.variables})
            res = self._start_build('base_dockerfile.jinja', values)
            if not res.get('result'):
                return res
            image_name = res.get('result').get('image_name')
        if self._config.container_config.get('full_stack'):
            values.update({
                'base_image_name': image_name, 'db_name': db_config.get('db_name'),
                'db_owner': db_config.get('db_owner'),
                'db_owner_passwd': db_config.get('db_owner_passwd')})
            res = self._start_build('dev_dockerfile.jinja', values)
        return res

    def _start_build(self, template, values):
        res = {}
        try:
            sha = self._create_image(template, values)
        except IOError as error:
            res.update({'error': utils.get_error_message(error)})
            return res
        except BuildError as error:
            msg_error = utils.get_error_message(error)
            if "This image has already been build with deployv" in msg_error:
                msg_error = ("An image that has already been built with deployv"
                             " can't be used to build another image.")
            res.update({'error': msg_error})
            return res
        res.update({'result': {'image_name': self._config.tag, 'image_sha': sha}})
        return res


def build_image(config, variables):
    """ Calls the build helper class with the needed parameters depending if
    a new full stack image, develop image or both will be created.
    If the config dictionary has both, build_image = true and postgres_container = true,
    first it will build a new image with the repos specified in the config and their
    oca dependencies, then that image will be used as base in order to build another one
    with the full stack tools.

    :param config: Configuration object with the format used by deployv.
    :return: dictionary with the new image created or an error.
    """
    build_res = {}
    config.check_config('build_image')
    _logger.debug('Starting the build image process with:')
    _logger.debug(json.dumps(config._deploy_config, sort_keys=True, indent=2))
    full_stack = config.container_config.get('full_stack')
    if not config.container_config.get('build_image') and not full_stack:
        build_res.update({'error': 'You must use the build_image and/or full_stack parameters'})
        return build_res
    _logger.debug('Building single image')
    variables.update({"main_repo_path": config.get_mainrepo_path()})
    build_class = BuildImage(config, variables)
    build_res = build_class.build()
    return build_res
