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

from venusclient.common import utils
from venusclient.v1 import basemodels

CREATION_ATTRIBUTES = basemodels.CREATION_ATTRIBUTES


class LogAnalyse(basemodels.BaseModel):
    model_name = "Analyse"


class AnalyseManager(basemodels.BaseModelManager):
    api_name = "search"
    base_url = "search"
    resource_class = LogAnalyse

    def analyse_log(self, group_name='', host_name='', module_name='',
                    program_name='', level='', start_time=0, end_time=20):
        url = '/v1/search/analyse/logs'

        params = {
            'group_name': group_name,
            'host_name': host_name,
            'module_name': module_name,
            'program_name': program_name,
            'level': level,
            'start_time': start_time,
            'end_time': end_time
        }
        url += utils.prepare_query_string(params)

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def typical_log(self, start_time, end_time, type):
        url = '/v1/search/typical/logs'
        params = {
            'start_time': start_time,
            'end_time': end_time,
            'type': type
        }
        url += utils.prepare_query_string(params)
        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))
