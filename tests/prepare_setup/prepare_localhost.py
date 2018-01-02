# !/usr/bin/env python2.7

import os
import subprocess
import shutil

from . import PrepareBase


class PrepareLocal(PrepareBase):
    '''
        This class is used for preparing environment on localhost for executing tests
    '''

    def __init__(self):
        super(PrepareLocal, self).__init__()
        self.module_path = os.path.abspath(__file__)

    def _create_dir(self, dir_path):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
            self.logger.log(self.module_path, "DEBUG", "folder {} has been successfully created".format(dir_path))

    def _remove_dir(self, dir_path):
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            self.logger.log(self.module_path, "DEBUG", "folder {} has been removed".format(dir_path))

    def execute_cmd(self, cmd):
        try:
            self.logger.log(self.module_path, "DEBUG", "execute cmd: {}".format(cmd))
            output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            self.logger.log(self.module_path, "DEBUG", "execute cmd: {}".format(output))
        except subprocess.CalledProcessError as ex:
            self.logger.log(self.module_path, "ERROR", "Could not execute command: {0} {1}".format(str(cmd), ex))
