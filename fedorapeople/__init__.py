import os

from helpers.helpers import parse_yml
from helpers.ssh_tool import SSHTool

FEDORAPEOPLE_CFG = 'configuration/fedorapeople_cfg.yml'
PATHS_CFG = 'configuration/paths.yml'


class PrepareRepoBase(object):
    _cfg_path = "/".join(os.path.abspath(__file__).split('/')[:-2]) + "/"
    _fedorapeople_cfg = parse_yml(_cfg_path + FEDORAPEOPLE_CFG)
    _paths_cfg = parse_yml(_cfg_path + PATHS_CFG)
    _ssh_session = None

    @classmethod
    def establish_ssh(cls):
        '''
            This method is used for prepare openstack image to run tests
        '''
        data = cls._fedorapeople_cfg['fedorapeople']
        result = None
        try:
            ssh = SSHTool(data['host'],
                          data['username'],
                          data['passwd'],
                          data['ssh_path'])

            if ssh.establish_connection():
                cls._ssh_session = ssh
                ssh.terminate_connection()
        except Exception, e:
            pass

        return result

    @property
    def fedoraproject(self):
        return PrepareRepoBase._paths_cfg['FEDORAPROJECT_PATH']

    @property
    def fedorapeople_cfg(self):
        return PrepareRepoBase._fedorapeople_cfg

    @property
    def upstream_git_path(self):
        return PrepareRepoBase._paths_cfg['UPSTREAM_GIT_PATH']


