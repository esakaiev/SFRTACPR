#!/usr/bin/env python2.7

import os
from . import PrepareBase


class PrepareOpenStack(PrepareBase):
    '''
        This class is used for preparing environment on Openstack server for executing tests
    '''

    _module_path = os.path.abspath(__file__)

    def __init__(self):
        super(PrepareOpenStack, self).__init__()

    def _create_dir(self, dir_path):
        cmd = "sudo python -c \"import os; os.makedirs('{0}')\"".format(dir_path)
        self.execute_cmd(cmd)

    def _remove_dir(self, dir_path):
        cmd = "sudo python -c \"import shutil; shutil.rmtree('{0}')\"".format(dir_path)
        self.execute_cmd(cmd)

    @property
    def _ssh(self):
        return PrepareOpenStack._ssh_sessions

    def execute_cmd(self, cmd):
        for image in self._ssh:
            self.logger.log(self.module_path, "DEBUG",
                            "Preparing setup for openstack image: {0}, cmd: {1}".format(image, cmd))
            self._ssh[image].send_ssh_command(cmd)

    def move_rhts_modules(self):
        for image in self._ssh:
            self._ssh[image].upload_files(r'/usr/local/bin/rhts-environment.sh', r'/usr/local/bin/rhts-environment.sh')

    @property
    def module_path(self):
        return PrepareOpenStack._module_path
