import sys

sys.path.append("..")  # # Adds higher directory to python modules path.
from test_executor import BaseExecutor
from helpers.ssh_tool import SSHTool
import os


class ClassicExecutor(BaseExecutor):
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
            >>>  classic = ClassicExecutor("/tmp/package_testing/upstream_first/attr/", ssh)
    '''

    def __init__(self, tests_path, paths_yml=None, ssh=None, playbook='tests.yml'):
        super(ClassicExecutor, self).__init__(tests_path, playbook)
        self._tag = 'classic'
        self._ssh = ssh  # # dict with ssh session to the servers
        self._paths_yml = paths_yml
        self.module_path = os.path.abspath(__file__)

    def _execute_cmd(self, cmd):
        stdout = None

        if not self._ssh:
            stdout = super(ClassicExecutor, self)._execute_cmd(cmd)
            self.logger.log(self.module_path, "INFO", "{0}".format(stdout))
        else:
            for image in self._ssh:
                self.logger.log(self.module_path, "INFO",
                                "Executing classic tests under {0} openstack image, cmd: {1}".format(image, cmd))
                stdin, stdout, stderr = self._ssh[image].send_ssh_command(cmd)
                self.logger.log(self.module_path, "INFO", "{0}, {1}, {2}".format(stdin, stdout, stderr))

        return stdout

    def parse_logs(self):
        if not self._ssh:
            super(ClassicExecutor, self).parse_logs()
        else:
            for image in self._ssh:
                super(ClassicExecutor, self).parse_logs_from_server(self._ssh, image)


if __name__ == "__main__":
    ssh = {"Fedora_Rawhide": SSHTool(r"10.8.xxx.xxx",
                                     r"fedora",
                                     r"some_password",
                                     r"//root//.ssh//some_key_name")}

    classic = ClassicExecutor("/tmp/package_testing/upstream_first/attr/", ssh)
    # classic.execute()

    # classic = ClassicExecutor("/tmp/package_testing/upstream_first/attr/")
    # classic.execute()
    classic.parse_logs()
