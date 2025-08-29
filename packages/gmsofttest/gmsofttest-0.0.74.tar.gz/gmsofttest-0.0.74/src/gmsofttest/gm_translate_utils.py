"""
Name : gm_translate_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2025-06-03 18:24
Desc:
"""
# -*- coding: utf-8 -*-
import os
from typing import Optional
from pprint import pprint
from alibabacloud_alimt20181012.client import Client as AlimtClient
from alibabacloud_credentials.models import Config as CredConfig
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_models
from alibabacloud_tea_util import models as util_models


class AliTranslateClient:
    """
    阿里云机器翻译工具类
    封装通用翻译功能，支持初始化配置和多种翻译方法
    """
    def __init__(self,
                 access_key_id: str = 'LTAI5tQzdUgvYNuddbH8Lk6w',
                 access_key_secret: str = 'MFwn6Dg3VkAb7inGPwP3eHx00OQmo5',
                 endpoint: str = 'mt.cn-hangzhou.aliyuncs.com'):
        """
                初始化翻译客户端

                :param access_key_id: 阿里云AccessKey ID
                :param access_key_secret: 阿里云AccessKey Secret
                :param endpoint: 服务端点，默认为通用翻译 endpoint
        """
        self.access_key_id = access_key_id or os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
        self.access_key_secret = access_key_secret or os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        self.endpoint = endpoint
        self._client = self.create_client()

    def create_client(self) -> AlimtClient:
        """
        使用硬编码 AccessKey 初始化客户端（仅限测试用途）
        """
        cred_config = CredConfig(
            type='access_key',
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        credential = CredentialClient(cred_config)

        config = open_api_models.Config(credential=credential)
        config.endpoint = 'mt.cn-hangzhou.aliyuncs.com'
        return AlimtClient(config)

    def translate_text(self,
        client: AlimtClient,
        source_text: str,
        source_lang: str = 'zh',
        target_lang: str = 'en'
    ) -> str:
        """
        调用通用翻译接口 TranslateGeneral
        :param client: 初始化好的 AlimtClient
        :param source_text: 要翻译的文本
        :param source_lang: 源语言代码（如 'zh' 表示中文）
        :param target_lang: 目标语言代码（如 'en' 表示英文）
        :return: 翻译结果
        """
        request = alimt_models.TranslateGeneralRequest(
            format_type='text',
            source_language=source_lang,
            target_language=target_lang,
            source_text=source_text
        )
        runtime = util_models.RuntimeOptions()

        try:
            response = self._client.translate_general_with_options(request, runtime)
            if response is not None and hasattr(response.body, 'to_map'):
                body_dict = response.body.to_map()
                code = body_dict.get('Code')
                message = body_dict.get('Message')
                data = body_dict.get('Data', {})

                if code == '200':
                    translation = data.get('Translated', '')
                    if translation:
                        return translation
                    else:
                        print("返回内容中未找到翻译字段")
                        return ""
                else:
                    print(f"API 返回错误：{message or code}")
                    return ""
            else:
                print("response 或 body 无效")
                return ""

        except Exception as error:
            print(f"发生异常：{error}")
            return ""


if __name__ == '__main__':
    # 初始化客户端（AK 已写入代码）
    client = AliTranslateClient()

    # 待翻译文本
    text_to_translate = "三级治理事项"

    # 执行翻译
    translated_text = client.translate_text(
        client=client,
        source_text=text_to_translate,
        source_lang='zh',
        target_lang='en'
    )

    # 输出结果
    print("原文本：", text_to_translate)
    print("翻译结果：", translated_text)