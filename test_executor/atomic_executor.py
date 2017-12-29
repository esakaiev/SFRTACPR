from test_executor import BaseExecutor


class AtomicExecutor(BaseExecutor):
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
            paths = {
                'TESTING_DIR': '/tmp/package_testing/upstream_first/',
                'UPSTREAM_GIT_PATH': 'https://upstreamfirst.fedorainfracloud.org/',
                'ATOMIC_IMAGE_URL': 'https://ftp-stud.hs-esslingen.de/pub/Mirrors/alt.fedoraproject.org/atomic/stable/Fedora-Atomic-26-20170707.1/CloudImages/x86_64/images/Fedora-Atomic-26-20170707.1.x86_64.qcow2',
                'STANDARD_INVENTORY_QCOW2': 'https://github.com/esakaiev/standard-inventory/blob/master/standard-inventory-qcow2',
            }
            >>>  atomic = AtomicExecutor("/tmp/package_testing/upstream_first/attr/", ssh)
        '''

    def __init__(self, tests_path, paths_yml=None, ssh=None, playbook='tests.yml'):
        super(AtomicExecutor, self).__init__(tests_path, playbook)
        self._tag = 'atomic'
        self._ssh = ssh
        self._paths_yml = paths_yml
        self._standard_inventory_qcow2 = 'standard-inventory-qcow2'

    @property
    def _obtain_atomic_qcow2(self):
        return "curl -Lo atomic.qcow2 {0}".format(self._paths_yml['ATOMIC_IMAGE_URL'])

    @property
    def _obtain_standard_inventory_qcow2(self):
        return "curl -Lo {0} {1}".format(self._standard_inventory_qcow2, self._paths_yml['STANDARD_INVENTORY_QCOW2'])

    @property
    def _exp_test_subj(self):
        return "export TEST_SUBJECTS=$PWD/atomic.qcow2"

    @property
    def _exp_extend_disk_size(self):
        return "export EXTEND_DISK_SIZE=8G"

    @property
    def _gen_exec_cmd(self):
        return "sudo ansible-playbook -i {0} -e {1} --tags={2} {3} {4} > {5} 2>&1".format(
            self._standard_inventory_qcow2,
            self._artifacts,
            self._tag,
            self._playbook,
            self._verbose,
            self._output_log)

    def execute(self):
        self._execute_cmd(self._exp_ansible_inventory)
        self._execute_cmd(self._obtain_atomic_qcow2)
        self._execute_cmd(self._exp_test_subj)
        self._execute_cmd(self._obtain_standard_inventory_qcow2)
        self._execute_cmd(self._exp_extend_disk_size)
        self._execute_cmd(self._gen_exec_cmd)


if __name__ == "__main__":
    paths = {
        'TESTING_DIR': '/tmp/package_testing/upstream_first/',
        'UPSTREAM_GIT_PATH': 'https://upstreamfirst.fedorainfracloud.org/',
        'ATOMIC_IMAGE_URL': 'https://ftp-stud.hs-esslingen.de/pub/Mirrors/alt.fedoraproject.org/atomic/stable/Fedora-Atomic-26-20170707.1/CloudImages/x86_64/images/Fedora-Atomic-26-20170707.1.x86_64.qcow2',
        'STANDARD_INVENTORY_QCOW2': 'https://github.com/esakaiev/standard-inventory/blob/master/standard-inventory-qcow2',
    }
    atomic = AtomicExecutor('/tmp/package_testing/upstream_first/attr/', paths)
    atomic.execute()
