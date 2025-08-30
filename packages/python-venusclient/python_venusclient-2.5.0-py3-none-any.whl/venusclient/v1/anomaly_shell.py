# Copyright 2023 Inspur
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


@utils.arg('--title',
           metavar='<title>',
           dest='title',
           help='The title of anomaly rule, required')
@utils.arg('--desc',
           metavar='<desc>',
           dest='desc',
           help='The description of anomaly rule, required')
@utils.arg('--keyword',
           metavar='<keyword>',
           dest='keyword',
           help='Keyword, only support exact-match at present, required')
@utils.arg('--log_type',
           metavar='<log_type>',
           dest='log_type',
           help='The type of log, flog is platform log, and slog is operate '
                'system log, required')
@utils.arg('--module',
           metavar='<module>',
           dest='module',
           help='Application module or service, required')
def do_add_anomaly_rule(cs, args):
    """add an anomaly rule"""
    endpoint = cs.anomaly.add_anomaly_rule(args.title, args.desc, args.keyword,
                                           args.log_type, args.module)
    print(endpoint)
    return endpoint


@utils.arg('id',
           metavar='<id>',
           help='The id of an anomaly rule.')
def do_get_anomaly_rule(cs, args):
    """get an anomaly rule"""
    endpoint = cs.anomaly.get_anomaly_rule(args.id)
    print(endpoint)
    return endpoint


def do_rule_list(cs, args):
    """get anomaly rule list"""
    endpoint = cs.anomaly.rule_list(args)
    print(endpoint)
    return endpoint


@utils.arg('id',
           metavar='<id>',
           help='The id of an anomaly rule.')
def do_delete_anomaly_rule(cs, args):
    """delete an anomaly rule"""
    endpoint = cs.anomaly.delete_anomaly_rule(args.id)
    print(endpoint)
    return endpoint


def do_record_list(cs, args):
    """get anomaly record list"""
    endpoint = cs.anomaly.rule_list(args)
    print(endpoint)
    return endpoint
