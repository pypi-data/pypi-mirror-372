# Copyright 2020 Inspur
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from venusclient.common import cliutils as utils


@utils.arg('group_name',
           metavar='<group_name>',
           help='Group name. "host_name" or "program_name".')
@utils.arg('--host_name',
           metavar='<host_name>',
           dest='host_name',
           help='Host name. optional')
@utils.arg('--module_name',
           metavar='<module_name>',
           dest='module_name',
           help='The module name. optional')
@utils.arg('--program_name',
           metavar='<program_name>',
           dest='program_name',
           help='The program name. optional')
@utils.arg('--level',
           metavar='<level>',
           dest='level',
           help="The level of log, such as 'error', 'info'. optional")
@utils.arg('--start_time',
           metavar='<start_time>',
           dest='start_time',
           help='The start timestamp of time frame. optional')
@utils.arg('--end_time',
           metavar='<end_time>',
           dest='end_time',
           help='The end timestamp of time frame. optional')
def do_analyse_log(cs, args):
    """get analyse log content"""
    endpoint = cs.analyse.analyse_log(args.group_name, args.host_name,
                                      args.module_name, args.program_name,
                                      args.level, args.start_time,
                                      args.end_time)
    print(endpoint)
    return endpoint


def do_typical_log(cs, args):
    """get typical log content"""
    endpoint = cs.analyse.typical_log(args)
    print(endpoint)
    return endpoint
