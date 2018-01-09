import shutil
import os
import subprocess
import sys

sys.path.append("..")

from logger.logger import Logger
from fedorapeople import PrepareRepoBase


class PrepareRepositoryOnFedoraPeople(PrepareRepoBase):
    '''
        This class can be used for preparing repo on fedorapeople for PR on pagure

            * package (`String`) - package name

        Usage:
            >>> prepare_pr =  PrepareRepositoryOnFedoraPeople('gdb')
            >>> prepare_repository.ssh_connect()
            >>> prepare_repository.upload_localrepo_to_fedorapeople() # will upload repository on fedorapeople.org
    '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, package):

        self._package = package
        self._local_dir = self.fedorapeople_cfg['paths']['local_dir']
        self._remote_dir = self.fedorapeople_cfg['paths']['remote_dir']

        self._logger = Logger()
        PrepareRepoBase.establish_ssh()

    def upload_localrepo_to_fedorapeople(self):
        # remove directory on remote if exists
        cmd = "rm -rf {0}{1}/public_git/{2}".format(self._remote_dir,
                                                    self.fedorapeople_cfg['fedorapeople']['username'],
                                                    self._package + '.git')
        self.ssh.send_ssh_command(cmd)
        self._logger.log(self._module_path, "DEBUG",
                         "folder {0} on remote host {1}  has been removed".format(self._package + '.git',
                                                                                  self.fedorapeople_cfg[
                                                                                      'fedorapeople']['host']))
        self.ssh.upload_files(self._local_dir + self._package + '.git',
                              "{0}{1}/public_git/{2}".format(self._remote_dir,
                                                             self.fedorapeople_cfg['fedorapeople']['username'],
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

    @property
    def module_path(self):
        return PrepareRepositoryOnFedoraPeople._module_path

    @property
    def ssh(self):
        return PrepareRepositoryOnFedoraPeople._ssh_session

    def create_repo(self):
        # create dir if not exists for fedorapeople repos:
        self._create_dir(self._local_dir)
        # removing directories, associated with previous PR for current package
        self._remove_dir(self._local_dir + self._package + '.git')
        self._remove_dir(self._local_dir + self._package)

        # 1. clone tests from upstreamfirst to fedorapeople dir
        cmd = "sudo git clone {0} {1}".format(self.upstream_git_path + self._package + '.git',
                                              self._local_dir + self._package + '_upstream/')
        self.execute_cmd(cmd)

        # 2. create local git repo for PR
        cmd = "sudo git init --bare {0}".format(self._local_dir + self._package + '.git')
        self.execute_cmd(cmd)

        # 3. clone local git repo
        cmd = "sudo git clone {0} {1}".format(self._local_dir + self._package + '.git',
                                              self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 4. Creating new_tests branch
        cmd = "cd {0}; sudo git checkout -b \"new_tests\"".format(self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 5. Adding tests in tests folder
        cmd = "cd {0}; mkdir tests; cp -r {1}* tests/; cd tests; rm -rf MIGRATED README.rst" \
            .format(self._local_dir + self._package,
                    self._local_dir + self._package + "_upstream/")
        self.execute_cmd(cmd)

        # 6. Adding and commit changes in branch
        cmd = "cd {0}; git add . ; git commit -m \" Adding tests from upstreamfirst to the  new_tests branch\"".format(
            self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 7. Adding remote repository:
        cmd = "cd {0}; git remote add fedoraproject {1} ".format(self._local_dir + self._package,
                                                                 self.fedoraproject + self._package)
        self.execute_cmd(cmd)

        # 8. Rebase on remote master
        cmd = "cd {0}; git fetch fedoraproject".format(self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 9. Rebase on remote master
        cmd = "cd {0}; git rebase fedoraproject/master".format(self._local_dir + self._package)
        self.execute_cmd(cmd)

        # 9 Push changes to the branch
        cmd = "cd {0}; git push --set-upstream origin new_tests -f".format(self._local_dir + self._package)
        self.execute_cmd(cmd)


if __name__ == "__main__":
    package = 'kmod'
    if len(sys.argv) > 1:
        package = sys.argv[1]

    prepare_repository = PrepareRepositoryOnFedoraPeople(package)
    prepare_repository.create_repo()
    prepare_repository.upload_localrepo_to_fedorapeople()
