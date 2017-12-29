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

import sys
from model.model import Model

if __name__ == "__main__":
    verbose = None
    if len(sys.argv) > 1 and (sys.argv[1] == '-v' or sys.argv[1] == '-vv' or sys.argv[1] == '-vvv'):
        print sys.argv[1]
        verbose = sys.argv[1]


    model = Model(verbose)
    model.prepare_environment()
    model.download_tests()
    model.execute_tests()




