import os

from . import BaseExecutor


class ContainerExecutor(BaseExecutor):
    '''
        This module is used for running tests with container tag
        :Input Arguments:

        * tests_path (`String`) - path to the local folder with tests
        * playbook (`String`) - path to the playbook

        :Example:
        ssh to openstack image or where it should be executed
        if ssh is None - tests will be executed on localhost

        >>>  container = ContainerExecutor("/tmp/package_testing/upstream_first/attr/")
    '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, path, playbook='tests.yml'):
        super(ContainerExecutor, self).__init__(path, playbook)
        self._tag = 'container'

    def parse_logs(self):
        if not self._ssh:
            super(ContainerExecutor, self).parse_logs()
        else:
            for image in self._ssh:
                super(ContainerExecutor, self).parse_logs_from_server(self._ssh, image)

    @property
    def _exp_test_subj(self):
        return "export TEST_SUBJECTS={}".format(self._paths_yml['DOCKER_TEST_SUBJECT'])

    @property
    def module_path(self):
        return ContainerExecutor._module_path

    def execute(self):
        self._execute_cmd(self._exp_ansible_inventory)
        self._execute_cmd(self._exp_test_subj)
        self._execute_cmd(self._gen_exec_cmd)


if __name__ == "__main__":
    container = ContainerExecutor("/tmp/package_testing/upstream_first/attr/")
    container.execute()
    container.parse_logs()
