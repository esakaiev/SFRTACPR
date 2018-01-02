#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Author: Eduard Sakaiev

#
# Copyright Red Hat Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# This file is part of Cockpit.
#

import os
import sys

import logger.logger as logger
from helpers.helpers import parse_yml

from tests.execute_tests import BaseExecutor
from tests.execute_tests.atomic_executor import AtomicExecutor
from tests.execute_tests.classic_executor import ClassicExecutor
from tests.execute_tests.container_executor import ContainerExecutor

from tests.prepare_setup.prepare_localhost import PrepareLocal
from tests.prepare_setup.prepare_openstack import PrepareOpenStack

OPENSTACK_CFG = 'configuration/openstack_cfg.yml'
INPUT_CFG = 'configuration/input_packages.yml'
PATHS_CFG = 'configuration/paths.yml'  # path to yaml file with all needed system paths
SETUP_SEPENDENCY = 'configuration/dependency.yml'  # path to yaml file with all needed system paths


class Model(object):
    # # initializing all classes here for execution of tests
    '''
        This module is main module, used for starting tests
        :param input_args:
        verbosity: ('String') - parameter for setting verbosity for output information for tests artifact
        :Example:
            >>> model = Model('-v')
            >>> model.prepare_environment()
            >>> model.download_tests()  # will download tests from required repository
            >>> model.execute_tests() # will execute tests on localhost or on remote, if openstack cfg is defined
    '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, verbosity=''):
        self._input_args = verbosity
        cfg_path = "/".join(os.path.abspath(__file__).split('/')[:-1]) + "/"
        self._paths_cfg = parse_yml(cfg_path + PATHS_CFG)
        self._input_data = parse_yml(cfg_path + INPUT_CFG)
        self._package_list = [[pkg, pkg_dict[pkg]] for pkg_dict in self._input_data for pkg in pkg_dict]
        self._prepare_systems = None

        self._prepare_systems = [PrepareLocal(),
                                 PrepareOpenStack()]

        self._executor = {'atomic': AtomicExecutor,
                          'classic': ClassicExecutor,
                          'container': ContainerExecutor}

        self.logger = logger.Logger()

    def prepare_environment(self):

        # 1. prepare environment
        for prepare in self._prepare_systems:
            prepare.install_dependencies()

    def download_tests(self):
        # 2. download tests
        for package in self._package_list:
            for prepare in self._prepare_systems:
                prepare.clean_artifacts(self._paths_cfg['ARTIFACTS'])
                prepare.download_tests(self._paths_cfg['UPSTREAM_GIT_PATH'] + package[0] + '.git',
                                       self._paths_cfg['TESTING_DIR'] + package[0] + '/')

    def execute_tests(self):
        for package in self._package_list:
            self.logger.log(self.module_path, "INFO", "Package under test: {0}".format(package[0]))
            if package[1] == []:
                executor = BaseExecutor(self._paths_cfg['TESTING_DIR'] + package[0] + '/')
                executor.execute()
                executor.parse_logs()
            else:
                for tag in package[1]:
                    self.logger.log(self.module_path, "INFO", "Executing tests for {} tag".format(tag))
                    executor = self._executor[tag](self._paths_cfg['TESTING_DIR'] + package[0] + '/')
                    executor.execute()
                    executor.parse_logs()
    @property
    def module_path(self):
        return Model._module_path


if __name__ == "__main__":
    verbose = None
    if len(sys.argv) > 1 and (sys.argv[1] == '-v' or sys.argv[1] == '-vv' or sys.argv[1] == '-vvv'):
        print sys.argv[1]
        verbose = sys.argv[1]

    model = Model(verbose)
    model.prepare_environment()
    model.download_tests()
    model.execute_tests()
