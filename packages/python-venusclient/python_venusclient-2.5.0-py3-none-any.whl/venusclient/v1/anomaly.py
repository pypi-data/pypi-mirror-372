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

from venusclient.common import utils
from venusclient.v1 import basemodels

CREATION_ATTRIBUTES = basemodels.CREATION_ATTRIBUTES


class LogAnomaly(basemodels.BaseModel):
    model_name = "Anomaly"


class AnomalyManager(basemodels.BaseModelManager):
    api_name = "anomaly"
    base_url = "anomaly"
    resource_class = LogAnomaly

    def add_anomaly_rule(self, title, desc, keyword, log_type, module):
        url = '/v1/anomaly/rule'

        body = {
            'title': title,
            'desc': desc,
            'keyword': keyword,
            'log_type': log_type,
            'module': module
        }

        try:
            resp, body = self.api.json_request('POST', url, body=body)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def get_anomaly_rule(self, rule_id):
        url = '/v1/anomaly/rule/' + rule_id

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def rule_list(self, title='', desc='', keyword='',
                  log_type='', module_name='', host_name='',
                  page_num=1, page_size=10):
        url = '/v1/anomaly/rule/list'

        params = {
            'title ': title,
            'desc': desc,
            'keyword': keyword,
            'log_type': log_type,
            'module_name': module_name,
            'flag': host_name,
            'page_num': page_num,
            'page_size': page_size
        }
        url += utils.prepare_query_string(params)

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def delete_anomaly_rule(self, rule_id):
        url = '/v1/anomaly/rule/' + rule_id

        try:
            resp, body = self.api.json_request('DELETE', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def record_list(self, title='', log_type='', module='',
                    start_time=0, end_time=0,
                    page_num=1, page_size=1):
        url = '/v1/anomaly/record/list'

        params = {
            'title ': title,
            'log_type': log_type,
            'module': module,
            'start_time': start_time,
            'end_time': end_time,
            'page_num': page_num,
            'page_size': page_size
        }
        url += utils.prepare_query_string(params)

        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))
