import os
import pyping
from helpers.helpers import parse_yml
from helpers.ssh_tool import SSHTool
from logger.logger import Logger

OPENSTACK_CFG = 'configuration/openstack_cfg.yml'
DEPENDENCY = 'configuration/dependency.yml'
PATHS_CFG = 'configuration/paths.yml'  # path to yaml file with all needed system paths


def deco(cls):
    cls.establish_ssh()
    return cls


@deco
class Base_Runner(object):
    _module_path = os.path.abspath(__file__)
    _cfg_path = "/".join(_module_path.split('/')[:-2]) + "/"
    _openstack_yml = parse_yml(_cfg_path + OPENSTACK_CFG)
    _dependency_cfg = parse_yml(_cfg_path + DEPENDENCY)
    _paths_yml = parse_yml(_cfg_path + PATHS_CFG)
    _ssh_sessions = {}
    _logger = Logger()

    @classmethod
    def establish_ssh(cls):
        '''
            This method is used for prepare openstack image to run tests
        '''
        result = {}
        for image in cls._openstack_yml['openstack']:
            image_data = cls._openstack_yml['openstack'][image]

            try:
                if cls.ping(image_data['ip']):
                    ssh = SSHTool(image_data['ip'],
                                  image_data['username'],
                                  image_data['passwd'],
                                  image_data['ssh_path'])
                    cls._ssh_sessions[image] = ssh
            except Exception, e:
                pass

        return result

    @classmethod
    def ping(cls, server_ip):
        '''
          Method for pinging of openstack images
        :return:
          ('Boolean') True | False
        '''
        is_pingable = False
        try:
            r = pyping.ping(server_ip)
            if r.ret_code == 0:
                is_pingable = True
            else:
                cls._logger.log(cls._module_path, "DEBUG", "Device {} is not pingable, skipping".format(server_ip))

        except Exception, exp:
            cls._logger.log(cls._module_path, "WARNING",
                            "Exception appeared during ping {0}:, {1}".format(server_ip, exp))

        return is_pingable

    @property
    def logger(self):
        return Base_Runner._logger
