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


class LogSearch(basemodels.BaseModel):
    model_name = "Searchs"


class SearchManager(basemodels.BaseModelManager):
    api_name = "search"
    base_url = "search"
    resource_class = LogSearch

    def get_log(self, host_name='', module_name='', program_name='', level='',
                user_id='', project_id='', querry='', start_time=0,
                end_time=20, page_num=1, page_size=15, index_type='flog'):
        url = '/v1/search/logs'

        params = {
            'host_name': host_name,
            'module_name': module_name,
            'program_name': program_name,
            'level': level,
            'user_id': user_id,
            'project_id': project_id,
            'querry': querry,
            'start_time': start_time,
            'end_time': end_time,
            'page_num': page_num,
            'page_size': page_size,
            'index_type': index_type
        }
        url += utils.prepare_query_string(params)

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def get_search_params(self, type, module_name, index_type='flog'):
        url = '/v1/search/params'

        qparams = {"type": type}
        if module_name:
            qparams["module_name"] = module_name
        if index_type:
            qparams["index_type"] = index_type
        url += utils.prepare_query_string(qparams)

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def get_instance_request_ids(self, args):
        url = 'v1/search/instance/request_ids'

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def do_get_analyse_logs(self, level='', start_time=0, end_time=0,
                            host_name='', module_name='', program_name='',
                            group_name='host_name'):
        url = 'v1/search/analyse/logs'

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

    def get_instance_callchain(self, request_id='', uuid=''):
        url = 'v1/search/instance/callchain'

        params = {
            'request_id': request_id,
            'uuid': uuid
        }
        url += utils.prepare_query_string(params)

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))
