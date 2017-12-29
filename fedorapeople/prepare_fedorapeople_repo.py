import sys
import shutil
import os
import subprocess

sys.path.append("..")  # # Adds higher directory to python modules path.

from logger.logger import Logger
from helpers.ssh_tool import SSHTool


class PrepareRepositoryOnFedoraPeople(object):
    '''
        This class can be used for preparing repo on fedorapeople for PR on pagure

            * upstream_git_path (`String`) - path to the git repository
            * package (`String`) - package name
            * fedorapeople_cfg (`Dictionary`) - dictionary with all data for ssh to fedorapeople


        :Example:
            fedorapeople_cfg = {
                'fedorapeople': {
                    'username': r'username',
                    'passwd': r'some_password',
                    'ssh_path': r'/root/.ssh/some_key',
                    'host': r'fedorapeople.org'},
                'paths': {
                    'local_dir': r'/tmp/package_testing/fedorapeople/',
                    'remote_dir': r'/home/fedora/'}}

            upstream_git_path = 'https://upstreamfirst.fedorainfracloud.org/'

        Usage:
            >>> prepare_pr =  PrepareRepositoryOnFedoraPeople(upstream_git_path, 'gdb', fedorapeople_cfg)
            >>> prepare_repository.create_repo() # will prepare repository with new_tests branch and tests in
                                                 #  tests folder on localhost
            >>> prepare_repository.ssh_connect()
            >>>prepare_repository.upload_localrepo_to_fedorapeople() # will upload repository on fedorapeople.org
    '''

    def __init__(self, upstream_git_path, package, fedorapeople_cfg):
        self._upstream_git_path = upstream_git_path
        self._package = package
        self._fedorapeople_cfg = fedorapeople_cfg
        self._local_dir = fedorapeople_cfg['paths']['local_dir']
        self._remote_dir = fedorapeople_cfg['paths']['remote_dir']

        self._logger = Logger()
        self._module_path = os.path.abspath(__file__)
        self.ssh = None

    def ssh_connect(self):
        self.ssh = SSHTool(self._fedorapeople_cfg['fedorapeople']['host'],
                           self._fedorapeople_cfg['fedorapeople']['username'],
                           self._fedorapeople_cfg['fedorapeople']['passwd'],
                           self._fedorapeople_cfg['fedorapeople']['ssh_path'])

    def upload_localrepo_to_fedorapeople(self):
        # remove directory on remote if exists
        cmd = "rm -rf {0}{1}/public_git/{2}".format(self._remote_dir,
                                                    self._fedorapeople_cfg['fedorapeople']['username'],
                                                    self._package + '.git')

        self.ssh.send_ssh_command(cmd)
        self._logger.log(self._module_path, "DEBUG",
                         "folder {0} on remote host {1}  has been removed".format(self._package + '.git',
                                                                                  self._fedorapeople_cfg[
                                                                                      'fedorapeople']['host']))
        self.ssh.upload_files(self._local_dir + self._package + '.git',
                              "{0}{1}/public_git/{2}".format(self._remote_dir,
                                                             self._fedorapeople_cfg['fedorapeople']['username'],
                                                             self._package + '.git'))

    def _remove_dir(self, dir_path):
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            self._logger.log(self._module_path, "DEBUG", "folder {} has been removed".format(dir_path))

    def _create_dir(self, dir_path):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
            self._logger.log(self._module_path, "DEBUG", "folder {0} has been successfully created".format(dir_path))
        else:
            self._logger.log(self._module_path, "DEBUG", "Local folder: {0} exists".format(dir_path))

    def execute_cmd(self, cmd):
        try:
            self._logger.log(self._module_path, 'INFO', 'Executing cmd: {0}'.format(cmd))
            output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            self._logger.log(self._module_path, "DEBUG", "execute cmd: \n {0}".format(output))
        except subprocess.CalledProcessError as ex:
            self._logger.log(self._module_path, "ERROR", "Could not execute command: {0} {1}".format(str(cmd), ex))

    def create_repo(self):
        # create dir if not exists for fedorapeople repos:
        self._create_dir(self._local_dir)
        # removing directories, associated with previous PR for current package
        self._remove_dir(self._local_dir + self._package + '.git')
        self._remove_dir(self._local_dir + self._package)

        # 1. clone tests from upstreamfirst to fedorapeople dir
        cmd = "sudo git clone {0} {1}".format(self._upstream_git_path + self._package + '.git',
                                              self._local_dir + self._package + '_upstream/')
        self.execute_cmd(cmd)

        # 2. create local git repo for PR
        cmd = "sudo git init --bare {0}".format(self._local_dir + self._package + '.git')
        self.execute_cmd(cmd)

        # 3. clone local git repo
        cmd = "sudo git clone {0} {1}".format(self._local_dir + self._package + '.git',
                                              self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 4. Initial commit
        cmd = "cd {0}; sudo touch {1}".format(self._local_dir + self._package, '.gitignore')
        self.execute_cmd(cmd)

        # 5. initial commit to the master branch"
        cmd = "cd {0}; sudo git add .".format(self._local_dir + self._package)
        self.execute_cmd(cmd)

        cmd = "cd {0} ; sudo git commit -m \"Initial commit, adding .gitignore to the master branch for {1} package \"".format(
            self._local_dir + self._package, self._package)
        self.execute_cmd(cmd)

        cmd = "cd {0}; sudo git push".format(self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 6. Creating new_tests branch
        cmd = "cd {0}; sudo git checkout -b \"new_tests\"".format(self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 7. Adding tests in tests folder
        cmd = "cd {0}; mkdir tests; cp -r {1}* tests/".format(self._local_dir + self._package,
                                                              self._local_dir + self._package + "_upstream/")
        self.execute_cmd(cmd)

        # 8. Adding and commit changes in branch
        cmd = "cd {0}; git add . ; git commit -m \" Adding tests from upstreamfirst to the  new_tests branch\"".format(
            self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 9 Push changes to the branch
        cmd = "cd {0}; git push --set-upstream origin new_tests".format(self._local_dir + self._package)
        self.execute_cmd(cmd)


if __name__ == "__main__":
    fedorapeople_cfg = {
        'fedorapeople': {
            'username': r'username',
            'passwd': r'some_passwd',
            'ssh_path': r'/root/.ssh/some_key',
            'host': r'fedorapeople.org'},
        'paths': {
            'local_dir': r'/tmp/package_testing/fedorapeople/',
            'remote_dir': r'/home/fedora/'}}
    prepare_repository = PrepareRepositoryOnFedoraPeople('https://upstreamfirst.fedorainfracloud.org/', 'gdb',
                                                         fedorapeople_cfg)
    prepare_repository.ssh_connect()
    prepare_repository.create_repo()
    prepare_repository.upload_localrepo_to_fedorapeople()
