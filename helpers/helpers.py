import yaml

import sys
import os

import logger.logger as logger


def parse_yml(cfg_path):
    '''
       This module is used for parse all data from configuration (yml) files
    :param cfg_path:
       * cfg_path (`String`) - path to the yml file
    :return:
       (`Dictionary')
    '''
    data = None
    with open(cfg_path) as input_cfg:
        try:
            data = yaml.load(input_cfg)
        except yaml.YAMLError as exc:
            module_path = os.path.abspath(__file__)
            logger.log(module_path, "ERROR", exc)

    return data


if __name__ == "__main__":
    parse_yml("configuration/paths.yml")
