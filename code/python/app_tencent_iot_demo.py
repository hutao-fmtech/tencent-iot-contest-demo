import json

from flask import Flask

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.iotexplorer.v20190423 import iotexplorer_client, models

cred = credential.Credential("你的腾讯云账号ID", "你的腾讯云账号Key")
httpProfile = HttpProfile()
httpProfile.endpoint = "iotexplorer.tencentcloudapi.com"

clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile

app = Flask(__name__)
light_state = 0


def light_state_set(dev_uuid, key_num, state):
    try:
        client = iotexplorer_client.IotexplorerClient(cred, "ap-guangzhou", clientProfile)
        req = models.ControlDeviceDataRequest()
        params = {'ProductId': '你的产品ID', 'DeviceName': dev_uuid, 'Data': "{\"key1_state\":1}"}

        if state == 1 and key_num == 1:
            params['Data'] = "{\"led_switch\":1}"

        if state == 0 and key_num == 1:
            params['Data'] = "{\"led_switch\":0}"

        req.from_json_string(json.dumps(params))

        resp = client.ControlDeviceData(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/light/api/v1.0/<string:dev_uuid>/<string:led_num>/', methods=['GET'])
def light_get_status(dev_uuid, led_num):
    return str(light_state)


@app.route('/light/api/v1.0/<string:dev_uuid>/<string:key_num>/<string:st>', methods=['POST'])
def light_set_status(dev_uuid, key_num, st):
    global light_state
    if st == 'on':
        light_state = 1
        light_state_set(dev_uuid, int(key_num), 1)
    elif st == 'off':
        light_state = 0
        light_state_set(dev_uuid, int(key_num), 0)

    return str(light_state)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
