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
AIHC resource pool client module.
"""
import json
from operator import truediv

from baidubce.http import http_methods
from baidubce.services.aihc.base.aihc_base_client import AIHCBaseClient


class ResourcePoolClient(AIHCBaseClient):
    """资源池相关接口客户端"""

    def DescribeResourcePools(self, resourcePoolType='common', keywordType=None, keyword=None, orderBy=None, order=None, pageNumber=1, pageSize=10):
        """
        获取资源池列表。

        :param resourcePoolType: 资源池类型（必填，Query参数）
            * 通用资源池：common
            * 托管资源池：dedicatedV2
            * 智算资源池：bhcmp
            * 边缘资源池：edge
        :type resourcePoolType: str
        :param keywordType: 资源池模糊查询字段，可选 [ resourcePoolName, resourcePoolId, ]，默认值为 resourcePoolName（可选，Query参数）
        :type keywordType: str
        :param keyword: 查询关键词，默认值为空字符串（可选，Query参数）
        :type keyword: str
        :param orderBy: 资源池查询排序字段，可选 [ resourcePoolName, resourcePoolId, createdAt ]，默认值为 resourcePoolName（可选，Query参数）
        :type orderBy: str
        :param order: 排序方式，可选 [ ASC, DESC ], ASC 为升序，DESC 为降序，默认值为 ASC（可选，Query参数）
        :type order: str
        :param pageNumber: 页码，默认值为1（可选，Query参数）
        :type pageNumber: int
        :param pageSize: 单页结果数，默认值为10（可选，Query参数）
        :type pageSize: int
        :return: 资源池列表及总数
        :rtype: baidubce.bce_response.BceResponse
        """
        path = '/'
        params = {
            'action': 'DescribeResourcePools',
            'resourcePoolType': resourcePoolType,
            'pageNumber': pageNumber,
            'pageSize': pageSize,
        }
        if keywordType is not None:
            params['keywordType'] = keywordType
        if keyword is not None:
            params['keyword'] = keyword
        if orderBy is not None:
            params['orderBy'] = orderBy
        if order is not None:
            params['order'] = order

        # print(params)
        return self._aihc_request(
            http_methods.GET,
            path,
            headers={},
            params=params
        )

    def DescribeResourcePool(self, resourcePoolId):
        """
        获取资源池详情。

        参考文档：https://cloud.baidu.com/doc/AIHC/s/Xmc1flhmc

        :param resourcePoolId: 资源池ID（必填，Query参数）
        :type resourcePoolId: str
        :return: 资源池详情
        :rtype: baidubce.bce_response.BceResponse
        """
        path = '/'
        params = {
            'action': 'DescribeResourcePool',
            'resourcePoolId': resourcePoolId,
        }
        return self._aihc_request(
            http_methods.GET,
            path,
            params=params
        )