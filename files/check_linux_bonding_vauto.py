#!/usr/bin/env python2

# File: check_linux_metrics.py
# URL: https://github.com/kxr/check_linux_metrics
# Author: Khizer Naeem 
# Email: khizernaeem@gmail.com
# Release 0.1: 20/05/2015
# Release 0.2: 02/06/2015
# Release 0.3: 16/07/2015
# Release 0.3.1: 06/10/2015
# Release 0.3.2: 31/01/2016
# Release 0.3.3: 16/03/2016
# Release 0.4.3: 22/08/2017
# 
#
#  Copyright (c) 2015 Khizer Naeem (http://kxr.me)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Local vAuto enhancements by david.rotthoff@vauto.com
#  2015.09.30  Added enhancement to split the standard network check into two different
#              complements -- one for bandwidth monitoring, the other for error monitoring
#  2015.09.30  Ensured that error monitoring is calculated as errors per minute
#  2015.09.30  Cleaned up how performance data was being captured for both of the new
#              check modules
#  2015.09.30  Defined the default interim directory where current state data is stored
#              as within the standard var directory of the vAuto install
#  2015.10.06  Cleaned up and standardized the output.
#  2015.10.06  Added aggregate values to the display and performance data.
#  2016.01.26  Modified code to rebuild the interim file if it is empty
#              and return a warning status
#  2016.01.26  Modified code to not return performance values when the 
#              result is negative and return an OK status
#  2016.01.31  Modified code to return detail CPU metrics
#  2016.03.16  Modified code read and use the speed of the network
#              interface in determining whether or not the load is
#              in warning or critical state.  Also modified the code
#              to compute the percent utilization and compare to
#              provided warning and critical utilization

import sys
import time
import os
import shutil

# INTERIM_DIR = '/usr/local/nagios/var/linux_metrics_vauto'
# INTERIM_DIR = '/tmp/linux_metrics_vauto'
# if not os.path.exists(INTERIM_DIR):
#     os.makedirs( INTERIM_DIR )

def check_network_bond ( interface=None, warn=None, crit=None ):
    """Check the state of the host network bonding devices"""
    interface_found = 0
    # status_code = 0
    # status_outp =''
    error_detail=''
    # status_message ='(OK)'
    # perfdata = ''

    # Read the bonding_masters file to find the network bond interfaces
    bonding_master_file = "/sys/class/net/bonding_masters"
    bond_interfaces = []

    if os.path.isfile( bonding_master_file ):
        with open(bonding_master_file, "r") as bonding_masters:
            bond_interfaces = bonding_masters.read().strip().split()
            print(bond_interfaces)
            # for line in bonding_masters.readlines():
            #     bond_interfaces += line.strip().split(" ")
    else:
        print("No network bond interfaces found")
        return

    # if os.path.isfile( bonding_master_file ):
    #     f = open( bonding_master_file, 'r' )
    #     try:
    #         for line in f:
    #             bond_interfaces = bond_interfaces + line.split()
    #     finally:
    #         f.close()
    #         for bond_interface in bond_interfaces:
    #             print 'Bond interface: %s' % bond_interface
    # else:
    #     print 'No network bond interfaces found'
    #     sys.exit(0)

    interfaces = {}
    for bond_interface in bond_interfaces:
        print("Processing bond %s" % bond_interface)
        with open("/sys/class/net/" + bond_interface + "/bonding/slaves",
                  "r") as interface_slaves:
            slave_up = list()
            slave_down = list()
            for line in interface_slaves.readlines():
                slaves = line.strip().split(" ")
                for slave in slaves:
                    with open(
                            "/sys/class/net/" + bond_interface + "/slave_" + slave + "/operstate",
                            "r") as status_file:
                        nic_status = status_file.readline().strip()
                        print("Slave %s is %s" % (slave, nic_status))
                        if nic_status == "up":
                            slave_up += [slave]
                        else:
                            slave_down += [slave]
            slave_status = (slave_up, slave_down)
            print(slave_status)
            interfaces[bond_interface] = slave_status

    print(interfaces)
    # Build a tuple of lists for each interface of up / down slaves

        #     # Check the status of each network bond interface
#     print("Checking bond interfaces %s" % bond_interfaces)
#     interfaces = {}
#     for bond_interface in bond_interfaces:
#         print('Processing bond %s' % bond_interface)
#         f = open('/sys/class/net/' + bond_interface + '/bonding/slaves', 'r')
#         try:
#             bond_slaves = []
#             for line in f:
#                 bond_slaves = bond_slaves + line.split()
#         finally:
#             f.close()
#             interfaces[bond_interface] = bond_slaves
#             print interfaces[bond_interface]
#         slaves = {}
#         for bond_slave in bond_slaves:
#             print 'Slave interface %s' % bond_slave
# #            slaves[bond_slave] = 'Up'
#
#             f = open('/sys/class/net/' + bond_interface + '/slave_' + bond_slave + '/operstate', 'r')
#             try:
#                 slave_status = []
#                 for line in f:
#                     slave_status = line.strip()
#             finally:
#                 f.close()
#                 slaves[bond_slave] = slave_status
#                 print interfaces[bond_interface]
        interfaces[bond_interface] = slaves
        print interfaces[bond_interface]
    print interfaces
    print status_message + ' ' + status_outp + '|' + perfdata
    sys.exit( status_code )


#####################
# Mainline function #
#####################
if __name__ == '__main__':
    if len( sys.argv ) > 1:
        # network bond status warn (count)  crit(count)
        if sys.argv[1] == 'network_bond':
            check_network_bond( )
        else:
            print ( 'What?' )
            sys.exit( 3 )
