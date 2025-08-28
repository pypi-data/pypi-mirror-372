# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""
AIHC queue client module.
"""
import json

from baidubce.http import http_methods
from baidubce.services.aihc.base.aihc_base_client import AIHCBaseClient


class QueueClient(AIHCBaseClient):
    """队列相关接口客户端"""

    def DescribeQueues(self, resourcePoolId, keywordType=None, keyword=None, pageNumber=1, pageSize=10):
        """
        获取队列列表。

        :param resourcePoolId: 资源池ID（必填，Query参数）
            * 通用资源池：cce-xxx
            * 托管资源池：aihc-xxx
            * 如果为"aihc-serverless"，则返回所有的托管资源池队列
        :type resourcePoolId: str
        :param keywordType: 队列模糊查询字段，可选 [ queueName ]，默认值为 queueName（可选，Query参数）
        :type keywordType: str
        :param keyword: 查询关键词，默认值为空字符串（可选，Query参数）
        :type keyword: str
        :param pageNumber: 页码，默认值为1（可选，Query参数）
        :type pageNumber: int
        :param pageSize: 单页结果数，默认值为10（可选，Query参数）
        :type pageSize: int
        :return: 队列列表及总数
        :rtype: baidubce.bce_response.BceResponse
        """
        path = '/'
        params = {
            'action': 'DescribeQueues',
            'resourcePoolId': resourcePoolId,
        }
        if keywordType is not None:
            params['keywordType'] = keywordType
        if keyword is not None:
            params['keyword'] = keyword
        if pageNumber is not None:
            params['pageNumber'] = pageNumber
        if pageSize is not None:
            params['pageSize'] = pageSize
        return self._aihc_request(
            http_methods.GET,
            path,
            params=params
        )

    def DescribeQueue(self, queueId):
        """
        获取队列详情。

        参考文档：https://cloud.baidu.com/doc/AIHC/s/Xmc1flhmc

        :param queueId: 队列ID（必填，Query参数）
        :type queueId: str
        :return: 队列详情
        :rtype: baidubce.bce_response.BceResponse
        """
        path = '/'
        params = {
            'action': 'DescribeQueue',
            'queueId': queueId,
        }
        return self._aihc_request(
            http_methods.GET,
            path,
            params=params
        )