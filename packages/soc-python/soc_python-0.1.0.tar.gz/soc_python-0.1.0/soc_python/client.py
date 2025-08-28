#!/usr/bin/env python3
import os
import requests
from urllib.parse import urljoin


class HttpClient:
    """HTTP客户端，支持通过环境变量配置"""
    
    def __init__(self):
        self.base_url = os.getenv('HTTP_BASE_URL', 'http://121.229.160.60:1687')
        self.token = os.getenv('HTTP_TOKEN', 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJydG0iLCJpZCI6MTExNzY4LCJuYW1lIjoibGl1emh1byIsImlhdCI6MTc1NjM0NjUxMSwiZXhwIjoxNzYxNTMwNTExfQ.U5egPaQHfPzVLGBu61XJXpQE7LVyDJt8zGDlgHrIA2o')

    def get_headers(self):
        """获取请求头"""
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'Content-Type': 'application/json',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'token': self.token
        }

    def post(self, endpoint, data=None, **kwargs):
        """发送POST请求"""
        url = urljoin(self.base_url, endpoint)
        headers = self.get_headers()

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                verify=False,
                **kwargs
            )
            return response
        except requests.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")