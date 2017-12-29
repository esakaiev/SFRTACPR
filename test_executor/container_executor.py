import sys
import os

sys.path.append("..")  # # Adds higher directory to python modules path.
from test_executor import BaseExecutor
from helpers.ssh_tool import SSHTool


class ContainerExecutor(BaseExecutor):
    '''
            This module is used for running tests with container tag
            :Input Arguments:

            * tests_path (`String`) - path to the local folder with tests
            * paths_yml (`Dictionary`) - dictionary with all required paths
            * ssh (`Dictionary`) - dictionary with all ssh session to required system under test
            * playbook (`String`) - path to the playbook

            :Example:
            ssh to openstack image or where it should be executed
            if ssh is None - tests will be executed on localhost
            ssh = {"Fedora_Rawhide": SSHTool(r"10.8.xxx.xxx",
                                         r"fedora",
                                         r"some_passwd",
                                         r"//root//.ssh//some_key_name")}
            >>>  container = ContainerExecutor("/tmp/package_testing/upstream_first/attr/", ssh)
        '''
    def __init__(self, path, paths_yml=None, ssh=None, playbook='tests.yml'):
        super(ContainerExecutor, self).__init__(path, playbook)
        self._tag = 'container'
        self._ssh = ssh
        self._paths_yml = paths_yml
        self.module_path = os.path.abspath(__file__)

    @property
    def _exp_test_subj(self):
        return "export TEST_SUBJECTS={}".format(self._paths_yml['DOCKER_TEST_SUBJECT'])

    def execute(self):
        self._execute_cmd(self._exp_ansible_inventory)
        self._execute_cmd(self._exp_test_subj)
        self._execute_cmd(self._gen_exec_cmd)

    def _execute_cmd(self, cmd):
        stdout = None
        if not self._ssh:
            stdout = super(ContainerExecutor, self)._execute_cmd(cmd)
        else:
            for image in self._ssh:
                self.logger.log(self.module_path, "INFO",
                                "Executing container tests under {0} openstack image, cmd: {1}".format(image, cmd))
                stdin, stdout, stderr = self._ssh[image].send_ssh_command(cmd)
                self.logger.log(self.module_path, "INFO", "{0}, {1}, {2}".format(stdin, stdout, stderr))

        return stdout

    def parse_logs(self):
        if not self._ssh:
            super(ContainerExecutor, self).parse_logs()
        else:
            for image in self._ssh:
                super(ContainerExecutor, self).parse_logs_from_server(self._ssh, image)


if __name__ == "__main__":
    ssh = {"Fedora_Rawhide": SSHTool("10.8.xxx.xxx",
                                     "fedora",
                                     "some_password",
                                     "/home/esaka/.ssh/some_key")}

    # container = ContainerExecutor("/tmp/package_testing/upstream_first/attr", ssh)
    # container.execute()

    container = ContainerExecutor("/tmp/package_testing/upstream_first/attr/")
    container.execute()
