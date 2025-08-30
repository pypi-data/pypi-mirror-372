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


@utils.arg('--host_name',
           metavar='<host_name>',
           dest='host_name',
           help='Host name')
@utils.arg('--module_name',
           metavar='<module_name>',
           dest='module_name',
           help='Module name')
@utils.arg('--program_name',
           metavar='<program_name>',
           dest='program_name',
           help='Program name')
@utils.arg('--level',
           metavar='<level>',
           dest='level',
           help='The level of log, such as error, info')
@utils.arg('--user_id',
           metavar='<user_id>',
           dest='user_id',
           help='The user id')
@utils.arg('--project_id',
           metavar='<project_id>',
           dest='project_id',
           help='The project id')
@utils.arg('--query',
           metavar='<query>',
           dest='query',
           help='The search query for elasticsearch')
@utils.arg('--start_time',
           metavar='<start_time>',
           dest='start_time',
           help='The start timestamp of time frame')
@utils.arg('--end_time',
           metavar='<end_time>',
           dest='end_time',
           help='The end timestamp of time frame')
@utils.arg('--page_num',
           metavar='<page_num>',
           dest='page_num',
           help='The page num, first and default is 1')
@utils.arg('--page_size',
           metavar='<page_size>',
           dest='page_size',
           help='The size of page, default is 10')
@utils.arg('--index_type',
           metavar='<index_type>',
           dest='index_type',
           help='The type of elasticsearch index, flog(default):Openstack log,'
                ' slog:host OS log')
def do_search_logs(cs, args):
    """search log content"""
    endpoint = cs.search.get_log(args.host_name, args.module_name,
                                 args.program_name, args.level, args.user_id,
                                 args.project_id, args.query, args.start_time,
                                 args.end_time, args.page_num,
                                 args.page_size, args.index_type)
    print(endpoint)
    return endpoint


@utils.arg('type',
           metavar='<type>',
           choices=['host_name', 'level', 'program_name', 'module_name'],
           help='The type of parameter, such as host_name, level, program_name'
                ', module_name')
@utils.arg('--module_name',
           metavar='<module_name>',
           dest='module_name',
           help='The module name.')
@utils.arg('--index_type',
           metavar='<index_type>',
           dest='index_type',
           choices=['flog', 'slog'],
           help='The type of elasticsearch index, flog(default):Openstack log,'
                ' slog:host OS log.')
def do_get_search_params(cs, args):
    """get search parameters of specified type"""
    endpoint = cs.search.get_search_params(args.type, args.module_name,
                                           args.index_type)
    print(endpoint)
    return endpoint


def do_get_instance_request_ids(cs, args):
    """get instance request id list."""
    endpoint = cs.search.get_instance_request_ids(args)
    print(endpoint)
    return endpoint


def do_get_analyse_logs(cs, args):
    """get search analyse logs"""
    endpoint = cs.search.do_get_analyse_logs(args)
    print(endpoint)
    return endpoint


@utils.arg('request_id',
           metavar='<request_id>',
           help='request id.')
@utils.arg('uuid',
           metavar='<uuid>',
           help='uuid.')
def do_get_instance_callchain(cs, args):
    """get instance callchain"""
    endpoint = cs.search.get_instance_callchain(args.request_id, args.uuid)
    print(endpoint)
    return endpoint
