import json
import os
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

class FeishuBot:
    def __init__(self, receive_id_type='email', receive_id='3306601284@qq.com'):
        self.app_id = os.environ.get('FEISHU_APP_ID')
        self.app_secret = os.environ.get('FEISHU_APP_SECRET')
        self.receive_id_type = receive_id_type  # 接受者id类型
        self.receive_id = receive_id  # 接受者id
        if not self.app_id or not self.app_secret:
            raise ValueError('FEISHU_APP_ID and FEISHU_APP_SECRET must be set')
        self.push_txt = ''
        # 创建client
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

    def send(self):
        """
        飞书机器人推送消息
        :return:
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(self.receive_id)
                          .msg_type("text")
                          .content(json.dumps({"text": self.push_txt}))
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        self.clear_push_txt()

    def append_push_txt(self, txt: str):
        self.push_txt += txt + '\n'
        return self

    def clear_push_txt(self):
        self.push_txt = ''
        return self


if __name__ == "__main__":
    fbot = FeishuBot()
    fbot.append_push_txt('=========123123=12=3=1=2==').append_push_txt('test').send()
