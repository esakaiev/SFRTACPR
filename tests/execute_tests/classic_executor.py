import os

from . import BaseExecutor


class ClassicExecutor(BaseExecutor):
    '''
            This module is used for running tests with container tag
            :Input Arguments:

            * tests_path (`String`) - path to the local folder with tests
            * playbook (`String`) - path to the playbook

            :Example:
            ssh to openstack image or where it should be executed
            if ssh is None - tests will be executed on localhost
            >>>  classic = ClassicExecutor("/tmp/package_testing/upstream_first/attr/")
    '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, tests_path, playbook='tests.yml'):
        super(ClassicExecutor, self).__init__(tests_path, playbook)
        self._tag = 'classic'

    @property
    def module_path(self):
        return ClassicExecutor._module_path


if __name__ == "__main__":
    classic = ClassicExecutor("/tmp/package_testing/upstream_first/attr/")
    classic.execute()
    classic.parse_logs()
