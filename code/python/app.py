import json
from builtins import bytes

from flask import Flask, jsonify, request

import base64

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.iotexplorer.v20190423 import iotexplorer_client, models

cred = credential.Credential("改成自己的账号密钥")
httpProfile = HttpProfile()
httpProfile.endpoint = "iotexplorer.tencentcloudapi.com"

clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile

app = Flask(__name__)
led_state = 0

def light_on(dev_uuid, key_num):
    try:
        client = iotexplorer_client.IotexplorerClient(cred, "ap-guangzhou", clientProfile)
        req = models.ControlDeviceDataRequest()
        params = {'ProductId': '自己创建的产品ID', 'DeviceName': dev_uuid, 'Data': "{\"led_state\":1}"}

        req.from_json_string(json.dumps(params))

        resp = client.ControlDeviceData(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)


def light_off(dev_uuid, key_num):
    try:
        client = iotexplorer_client.IotexplorerClient(cred, "ap-guangzhou", clientProfile)
        req = models.ControlDeviceDataRequest()
        params = {'ProductId': '自己创建的产品ID', 'DeviceName': dev_uuid, 'Data': "{\"led_state\":0}"}

        req.from_json_string(json.dumps(params))

        resp = client.ControlDeviceData(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/light/api/v1.0/<string:dev_uuid>/<string:led_num>/<string:st>', methods=['GET', 'PUT', 'POST'])
def light_set_status(dev_uuid, st):
    global light_status
    if st == 'on':
        led_state = 1
        light_on(dev_uuid, int(led_num))
    elif st == 'off':
        led_state = 0
        light_off(dev_uuid, int(led_num))

    return str(led_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)

