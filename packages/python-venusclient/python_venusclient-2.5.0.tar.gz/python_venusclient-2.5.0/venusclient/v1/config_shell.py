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


def do_get_log_storage_days(cs, args):
    """get the days of saved logs in elasticsearch(unit day)."""
    endpoint = cs.config.get_days()
    print(endpoint)
    return endpoint


@utils.arg('id',
           metavar='<id>',
           help='The id of custom config')
@utils.arg('value',
           metavar='<value>',
           help='The value set to custom config')
def do_set_custom_config(cs, args):
    """set the custom config."""
    endpoint = cs.config.set_custom_config(args.id, args.value)
    print(endpoint)
    return endpoint
