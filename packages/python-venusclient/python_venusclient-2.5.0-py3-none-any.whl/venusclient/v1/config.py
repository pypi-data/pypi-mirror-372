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

from venusclient.v1 import basemodels


CREATION_ATTRIBUTES = basemodels.CREATION_ATTRIBUTES


class LogConfig(basemodels.BaseModel):
    model_name = "Configs"


class ConfigManager(basemodels.BaseModelManager):
    api_name = "configs"
    base_url = "configs"
    resource_class = LogConfig

    def get_days(self):
        url = '/v1/custom_config'
        try:
            resp, body = self.api.json_request('GET', url)
            return body
        except Exception as e:
            raise RuntimeError(str(e))

    def set_custom_config(self, config_id, value):
        """Set custom config to the specified value.

        :param config_id: The ID of the custom config
        :param value: The value to set
        :returns: The result of the set action.
        """
        url = '/v1/custom_config'
        body = {'id': config_id,
                'value': value}
        try:
            resp, body = self.api.json_request('POST', url, body=body)
            return body
        except Exception as e:
            raise RuntimeError(str(e))
