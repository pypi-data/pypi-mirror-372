# -*- coding: utf-8 -*-

"""
@Project : luke_oss_api 
@File    : __init__.py.py
@Date    : 2025/8/29 15:42:28
@Author  : luke
@Desc    : 
"""
import requests


class LukeOssBox:
    def __init__(self, base_url, auth):
        self.base_url = base_url
        self.auth = auth
        self.headers = {
            "Authorization": f"Bearer {self.auth}"
        }

    def upload_file(self, file_path):
        """上传到oss"""
        with open(file_path, 'rb') as f:
            files = {
                'file': f
            }
            response = requests.post(
                f"{self.base_url}/api/v1/files/upload",
                headers=self.headers, files=files, timeout=15
            )
            print(response.text)
            res_json = response.json()
            if 'data' in res_json:
                if 'download_url' in res_json['data']:
                    res_json['data']['download_url'] = f"{self.base_url}{res_json['data']['download_url']}"
                if 'preview_url' in res_json['data']:
                    res_json['data']['preview_url'] = f"{self.base_url}{res_json['data']['preview_url']}"
            return res_json
