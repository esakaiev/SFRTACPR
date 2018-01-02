import os

from helpers.helpers import parse_yml
from helpers.ssh_tool import SSHTool

OPENSTACK_CFG = 'configuration/openstack_cfg.yml'
DEPENDENCY = 'configuration/dependency.yml'
PATHS_CFG = 'configuration/paths.yml'  # path to yaml file with all needed system paths


class Base_Runner(object):
    _cfg_path = "/".join(os.path.abspath(__file__).split('/')[:-2]) + "/"
    _openstack_yml = parse_yml(_cfg_path + OPENSTACK_CFG)
    _dependency_cfg = parse_yml(_cfg_path + DEPENDENCY)
    _paths_yml = parse_yml(_cfg_path + PATHS_CFG)
    _ssh_sessions = {}

    @classmethod
    def establish_ssh(cls):
        '''
            This method is used for prepare openstack image to run tests
        '''
        result = {}
        for image in cls._openstack_yml['openstack']:
            image_data = cls._openstack_yml['openstack'][image]

            try:
                ssh = SSHTool(image_data['ip'],
                              image_data['username'],
                              image_data['passwd'],
                              image_data['ssh_path'])

                if ssh.establish_connection():
                    cls._ssh_sessions[image] = ssh
                    ssh.terminate_connection()
            except Exception, e:
                pass

        return result
