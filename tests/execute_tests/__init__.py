import subprocess
import os

from tests import Base_Runner
from logger.logger import Logger


class BaseExecutor(Base_Runner):
    '''
        This class is used for executing all ansible tests with tags=all

        :Input Arguments:
        * path (`String`) - path to the package tests
        * playbook (`String') - path to the playbook


        :Example:
        >>> BaseExecutor('/home/esaka/package_testing/upstream_first/shadow-utils/', 'tests.yml')

    '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, path, playbook='tests.yml'):
        self._tag = 'all'
        self._artifacts = path + 'artifacts/'
        self._playbook = path + playbook
        self._verbose = ''
        self._output_log = 'output.log'
        self.logger = Logger()
        Base_Runner.establish_ssh()

    def _execute_cmd(self, cmd):
        stdout = None
        if self._tag in self._openstack_cfg['tags'] and self._ssh:
            for image in self._ssh:
                self.logger.log(self.module_path, "INFO",
                                "Executing {0} tests under {1} openstack image, cmd: {2}".format(self._tag, image, cmd))
                stdin, stdout, stderr = self._ssh[image].send_ssh_command(cmd)
                self.logger.log(self.module_path, "INFO", "{0}, {1}, {2}".format(stdin, stdout, stderr))
        else:
            try:
                self.logger.log(self.module_path, "INFO", "Starting cmd: {}".format(cmd))
                stdout = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                self.logger.log(self.module_path, "INFO", "Output: {}".format(stdout))
            except subprocess.CalledProcessError as ex:
                self.logger.log(self.module_path, "ERROR", "Exception appeared: {}".format(ex))
        return stdout

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        if verbose == '-v' or verbose == '-vv' or verbose == '-vvv':
            self._verbose = verbose
        else:
            self.logger.log(self.module_path, "WARNING", "Verbose, wrong format")

    @property
    def artifacts(self):
        return self.artifacts

    @artifacts.setter
    def artifact(self, artifacts):
        self._artifacts = artifacts

    @property
    def _exp_ansible_inventory(self):
        return "ANSIBLE_INVENTORY=$(test -e inventory && echo inventory || echo /usr/share/ansible/inventory)"

    @property
    def _gen_exec_cmd(self):
        return "ansible-playbook -e {0} --tags={1} {2} {3} > {4} 2>&1".format(self._artifacts,
                                                                              self._tag,
                                                                              self._playbook,
                                                                              self._verbose,
                                                                              self._output_log)

    @property
    def _ssh(self):
        return BaseExecutor._ssh_sessions

    @property
    def _paths_yml(self):
        return Base_Runner._paths_yml

    @property
    def _openstack_cfg(self):
        return Base_Runner._openstack_yml

    @property
    def module_path(self):
        return BaseExecutor._module_path

    def execute(self):
        self._execute_cmd("sudo {0} {1}".format(self._exp_ansible_inventory,
                                                self._gen_exec_cmd))

    def parse_logs(self):
        with open(self._artifacts + 'test.log') as log:
            self.test_log = log.readlines()

        for test_status in self.test_log:
            self.logger.log(self.module_path, "INFO", "Test status: {0}".format(test_status))

        with open(self._output_log) as log:
            self.output = log.readlines()

        self.logger.log(self.module_path, "INFO", "Output: {0}".format(self.output[-2]))

    def parse_logs_from_server(self, ssh, image):
        self.logger.log(self.module_path, "INFO",
                        "image: {0}, command: cat {1}".format(image, self._artifacts + 'test.log'))
        stdin, stdout, stderr = ssh[image].send_ssh_command("cat {0}".format(self._artifacts + 'test.log'))

        self.logger.log(self.module_path, "INFO",
                        "image: {0}, command: tail {1}".format(image, self._output_log))
        stdin, stdout, stderr = ssh[image].send_ssh_command("tail {0}".format(self._output_log))


if __name__ == '__main__':
    base_exec = BaseExecutor('/home/esaka/package_testing/upstream_first/shadow-utils/')
    base_exec.execute()
