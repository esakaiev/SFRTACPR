import os
from . import BaseExecutor


class AtomicExecutor(BaseExecutor):
    '''
            This module is used for running tests with container tag
            :Input Arguments:

            * tests_path (`String`) - path to the local folder with tests
            * playbook (`String`) - path to the playbook

            :Example:
            ssh to openstack image or where it should be executed
            if ssh is None - tests will be executed on localhost

            >>>  atomic = AtomicExecutor("/tmp/package_testing/upstream_first/attr/")
        '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, tests_path, playbook='tests.yml'):
        super(AtomicExecutor, self).__init__(tests_path, playbook)
        self._tag = 'atomic'
        self._standard_inventory_qcow2 = 'standard-inventory-qcow2'

    @property
    def _obtain_atomic_qcow2(self):
        return "curl -Lo atomic.qcow2 {0}".format(AtomicExecutor._paths_yml['ATOMIC_IMAGE_URL'])

    @property
    def _obtain_standard_inventory_qcow2(self):
        return "curl -Lo {0} {1}".format(self._standard_inventory_qcow2,
                                         AtomicExecutor._paths_yml['STANDARD_INVENTORY_QCOW2'])

    @property
    def _exp_test_subj(self):
        return "TEST_SUBJECTS=$PWD/atomic.qcow2"

    @property
    def _exp_extend_disk_size(self):
        return "EXTEND_DISK_SIZE=8G"

    @property
    def _gen_exec_cmd(self):
        return "ansible-playbook -i {0} -e {1} --tags={2} {3} {4} > {5} 2>&1".format(
            self._standard_inventory_qcow2,
            self._artifacts,
            self._tag,
            self._playbook,
            self._verbose,
            self._output_log)

    @property
    def module_path(self):
        return AtomicExecutor._module_path

    def execute(self):
        self._execute_cmd(self._obtain_atomic_qcow2)
        self._execute_cmd(self._obtain_standard_inventory_qcow2)
        self._execute_cmd("sudo {0} {1} {2} {3}".format(self._exp_ansible_inventory,
                                                        self._exp_test_subj,
                                                        self._exp_extend_disk_size,
                                                        self._gen_exec_cmd))


if __name__ == "__main__":
    atomic = AtomicExecutor('/tmp/package_testing/upstream_first/attr/')
    atomic.execute()
    atomic.parse_logs()
