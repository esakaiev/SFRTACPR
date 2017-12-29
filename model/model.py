import sys
import os

sys.path.append("..")  # # Adds higher directory to python modules path.

from helpers.helpers import parse_yml
from test_executor import BaseExecutor
from test_executor.atomic_executor import AtomicExecutor
from test_executor.classic_executor import ClassicExecutor
from test_executor.container_executor import ContainerExecutor
from preparations.prepare_localhost import PrepareLocal
from preparations.prepare_openstack import PrepareOpenStack
import logger.logger as logger

cfg_path = "/".join(os.path.abspath(__file__).split('/')[:-2]) + "/"
OPENSTACK_CFG = cfg_path + 'configuration/openstack_cfg.yml'
INPUT_CFG = cfg_path + 'configuration/input_packages.yml'
PATHS_CFG = cfg_path + 'configuration/paths.yml'  # path to yaml file with all needed system paths
SETUP_SEPENDENCY = cfg_path + 'configuration/dependency.yml'  # path to yaml file with all needed system paths


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

    def __init__(self, verbosity=''):
        self._input_args = verbosity
        self._paths_cfg = parse_yml(PATHS_CFG)
        self._input_data = parse_yml(INPUT_CFG)
        self._openstack_cfg = parse_yml(OPENSTACK_CFG)
        self._dependency = parse_yml(SETUP_SEPENDENCY)
        self._package_list = [[pkg, pkg_dict[pkg]] for pkg_dict in self._input_data for pkg in pkg_dict]
        self._prepare_systems = None
        self._ssh = None

        self._prepare_systems = [PrepareLocal(self._paths_cfg['TESTING_DIR'],
                                              self._paths_cfg['UPSTREAM_GIT_PATH']),
                                 PrepareOpenStack(self._paths_cfg['TESTING_DIR'],
                                                  self._paths_cfg['UPSTREAM_GIT_PATH'],
                                                  self._openstack_cfg)]

        self._ssh = self._prepare_systems[1].ssh

        self._executor = {'atomic': AtomicExecutor,
                          'classic': ClassicExecutor,
                          'container': ContainerExecutor}

        self.logger = logger.Logger()
        self.module_path = os.path.abspath(__file__)

    def prepare_environment(self):

        # 1. prepare environment
        for prepare in self._prepare_systems:
            prepare.install_dependencies()

    def download_tests(self):
        # 2. download tests
        for package in self._package_list:
            for prepare in self._prepare_systems:
                prepare.clean_artifacts(self._paths_cfg['ARTIFACTS'])
                prepare.download_tests(package[0])

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
                    executor = self._executor[tag](self._paths_cfg['TESTING_DIR'] + package[0] + '/',
                                                   self._paths_cfg,
                                                   self._ssh)
                    executor.execute()
                    executor.parse_logs()


if __name__ == "__main__":
    model = Model()
    model.prepare_environment()
    model.download_tests()
    model.execute_tests()
