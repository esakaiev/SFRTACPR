#!/usr/bin/env python2.7

import pyping
from helpers.ssh_tool import SSHTool
from preparations import PrepareBase
import os


class PrepareOpenStack(PrepareBase):
    '''
        This class is used for preparing environment on Openstack server for executing tests

        :Input arguments:

        * testing_dir (`String`) - path to the directory, where should be located folders with tests for packages
        * upstream_git_path ('String') - path to the git repository
        * openstack_data ('Dictionary') - dictionary with all required data for ssh to the server

        :Example:


        testing_dir = '/tmp/package_testing/upstream_first/'
        upstream_git_path = 'https://upstreamfirst.fedorainfracloud.org/'
        openstack_data = {'tags': [clasic, container],

                        'openstack': {
                          'Fedora27': {'ssh_path': '/root/.ssh/some_key',
                                      'ip': '10.8.xxx.xxx',
                                      'username': 'fedora',
                                      'passwd': 'some_password'}}}

    '''
    def __init__(self, testing_dir, upstream_git_path, openstack_data):
        super(PrepareOpenStack, self).__init__(testing_dir, upstream_git_path)
        self._ostack_data = openstack_data
        self._ssh = {}
        self._prepare_setup()
        self.module_path = os.path.abspath(__file__)

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

    def _prepare_setup(self):
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

    def _create_dir(self, dir_path):
        cmd = "sudo python -c \"import os; os.makedirs('{0}')\"".format(dir_path)
        self.execute_cmd(cmd)

    def _remove_dir(self, dir_path):
        cmd = "sudo python -c \"import shutil; shutil.rmtree('{0}')\"".format(dir_path)
        self.execute_cmd(cmd)

    @property
    def ssh(self):
        return self._ssh

    def execute_cmd(self, cmd):
        for image in self._ssh:
            stdin, stdout, stderr = self._ssh[image].send_ssh_command(cmd)
            self.logger.log(self.module_path, "DEBUG",
                            "Preparing setup for openstack image: {0}, cmd: {1}".format(image, cmd))
            self.logger.log(self.module_path, "DEBUG", stdout)
