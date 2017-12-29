import os
from abc import ABCMeta
from logger.logger import Logger
from helpers.helpers import parse_yml


class PrepareBase(object):
    '''
        This is base abstract class for preparing environment functionality
    '''

    def __init__(self, testing_dir, upstream_git_path):
        __metaclass__ = ABCMeta
        self._testing_dir = testing_dir
        self._upstr_git_path = upstream_git_path
        self.logger = Logger()

    def install_dependencies(self):
        '''
           This method is used for preparing setup for running the tests from upstreamfirst
        '''
        cfg_path = "/".join(os.path.abspath(__file__).split('/')[:-2]) + "/"
        dependency = parse_yml(cfg_path + 'configuration/dependency.yml')

        for package in dependency:
            # Make sure the dependency is installed:
            cmd = "sudo dnf install {}".format(package)
            self.execute_cmd(cmd)

    def _create_dir(self, dir_path):
        pass

    def _remove_dir(self, dir_path):
        pass

    def download_tests(self, package):
        '''
            This method is used for clonning tests from upstreamfirst repo
            : Return value:
            - path [ 'String' ] - path to the tests in testing dir
        '''
        self._create_dir(self._testing_dir)
        self._remove_dir(self._testing_dir + package + '/')

        upstream_git_path = self._upstr_git_path + package + '.git'
        cmd = "sudo git clone {0} {1}".format(upstream_git_path, self._testing_dir + package + '/')

        self.execute_cmd(cmd)

        return self._testing_dir + package + '/'

    def execute_cmd(self, cmd):
        pass

    def clean_artifacts(self, artifacts_path):
        self._remove_dir(artifacts_path)
