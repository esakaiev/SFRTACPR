import subprocess
import os
import pyping
from logger.logger import Logger
from helpers.helpers import parse_yml
from helpers.ssh_tool import SSHTool

cfg_path = "/".join(os.path.abspath(__file__).split('/')[:-2]) + "/"
INPUT_CFG = cfg_path + 'configuration/input_packages.yml'
OPENSTACK_CFG = cfg_path + 'configuration/openstack_cfg.yml'


class BaseExecutor(object):
    '''
        This class is used for executing all ansible tests with tags=all

        :Input Arguments:
        * path (`String`) - path to the pacakge tests
        * playbook (`String') - path to the playbook


        :Example:
        >>> BaseExecutor('/home/esaka/package_testing/upstream_first/shadow-utils/', 'tests.yml')

    '''

    def __init__(self, path, playbook='tests.yml'):
        self._path = path  # path to the folder with tests
        self._tag = 'all'
        self._input_cfg = parse_yml(INPUT_CFG)
        self._artifacts = path + 'artifacts/'
        self._playbook = path + playbook
        self._verbose = ''
        self._images = {}
        self._ssh = {}
        self._output_log = 'output.log'
        self.logger = Logger()
        self.module_path = os.path.abspath(__file__)

    def _execute_cmd(self, cmd):
        stdout = None
        try:
            self.logger.log(self.module_path, "INFO", "Starting cmd: {}".format(cmd))
            stdout = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
            self.logger.log(self.module_path, "INFO", "Output: {}".format(stdout))
        except subprocess.CalledProcessError as ex:
            self.logger.log(self.module_path, "ERROR", "Exception appeared: {}".format(ex))
        return stdout

    def _ping(self, server_ip):
        '''
          Method for pinging openstack images
        :return:
          ('Boolean') True | False
        '''
        is_pingable = False
        try:
            r = pyping.ping(server_ip)
            if r.ret_code == 0:
                is_pingable = True

        except Exception, exp:
            self.logger.log(self.module_path, "WARNING", "Device {} is not pingable, skipping".format(server_ip))

        return is_pingable

    def _check_images(self):
        '''
            This method is used for prepare openstack image to run tests

            :return:
            None
        '''
        for image in self._ostack_data['openstack']:
            image_data = self._ostack_data['openstack'][image]

            if self._ping(image_data['ip']):
                ssh = SSHTool(image_data['ip'],
                              image_data['username'],
                              image_data['passwd'],
                              image_data['ssh_path'])

                if ssh.establish_connection():
                    self._ssh[image] = ssh
                    self._ssh[image].terminate_connection()

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        if verbose == '-v' or verbose == '-vv' or verbose == '-vvv':
            self._verbose = verbose
        else:
            print "Verbose, wrong format"

    @property
    def artifacts(self):
        return self.artifacts

    @artifacts.setter
    def artifact(self, artifacts):
        self._artifacts = artifacts

    @property
    def _exp_ansible_inventory(self):
        return "export ANSIBLE_INVENTORY=$(test -e inventory && echo inventory || echo /usr/share/ansible/inventory)"

    @property
    def _gen_exec_cmd(self):
        return "sudo ansible-playbook -e {0} --tags={1} {2} {3} > {4} 2>&1".format(self._artifacts,
                                                                                   self._tag,
                                                                                   self._playbook,
                                                                                   self._verbose,
                                                                                   self._output_log)

    def execute(self):
        self._execute_cmd(self._exp_ansible_inventory)
        self._execute_cmd(self._gen_exec_cmd)

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
