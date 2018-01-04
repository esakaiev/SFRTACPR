from tests import Base_Runner


class PrepareBase(Base_Runner):
    '''
        This is base abstract class for preparing environment functionality
    '''

    def install_dependencies(self):
        '''
           This method is used for preparing setup for running the tests from upstreamfirst
        '''

        for package in self.dependency:
            # Make sure the dependency is installed:
            cmd = "sudo dnf -y install {}".format(package)
            self.execute_cmd(cmd)

    def _create_dir(self, dir_path):
        pass

    def _remove_dir(self, dir_path):
        pass

    def download_tests(self, git_url, target_dir):
        '''
            This method is used for clonning tests from upstreamfirst repo
        '''
        testing_dir = "/".join(target_dir.split('/')[:-1])
        self._create_dir(testing_dir)
        self._remove_dir(target_dir)

        cmd = "sudo git clone {0} {1}".format(git_url, target_dir)
        self.execute_cmd(cmd)

    def execute_cmd(self, cmd):
        pass

    def clean_artifacts(self, artifacts_path):
        self._remove_dir(artifacts_path)

    @property
    def dependency(self):
        return PrepareBase._dependency_cfg
