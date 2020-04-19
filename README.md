# 【IoT应用创新大赛】基于LoRa的智慧办公场景方案

随着物联网技术的发展及越来越多的应用需求，促成了整个物联网产业链的基础设的施快速发展。以腾讯、阿里为首的头部云计算企业，纷纷推出了物联网设备接入的基础设施（嵌入式系统 + 物联网管理平台），极大的方便了物联网应用场景的落地。在此借【腾讯云loT创新大赛】机会，跟各位从业者一起交流。

本次交流的场景是：智慧办公的场景，实际是传统智能家居延伸。

传统智能家居的组网方案，如Wi-Fi，Zigbee，蓝牙等在终端设备的数量和维护的复杂性，在办公环境大量设备的情况下，变得更加困难。办公场景下的“智能家居”特点是：终端数量大，数据量小、统一管理、旧改走线麻烦，LoRa 作为距离远、容量大、星形网络，正好满足智慧办公场景的需求，也是本方案选择LoRa作为底层无线通信技术原因。

#### 零：必要资源
本着 **可重复、可验证** 的原则，本方案尽量选择腾讯云为大家准备的硬件资源。唯一额外使用的硬件资源就是树莓派，网上有多种型号可以选择，大家可以在淘宝上【*树莓派*】关键字，根据自己的需求购买。

##### 0.0 硬件组成
- 树莓派4B+：用于运行HomeBridge服务、腾讯云 Iot-Explorer 通信服务
- iPhone（iOS 10以上版本）：识别语音指令
- P-NUCLEO-LRWAN3 开发套件：LoRaWAN 终端执行节点、LoRaWAN 网关接入腾讯云。


##### 0.1 语言 & 应用 & 插件
- **语言**

> 1. Python ：逻辑控制模块开发，连接腾讯云Iot-Explore 与 homebridge。
> 2. C ：LoRaWAN 节点功能开发。
> 3. JavaScript ：腾讯云Iot-Explore 二进制数据解析。

- **应用**

> 1. homebridge: 模拟苹果 HomeKit 协议，桥接非苹果认证设备。
> 2. iOS 家庭App：关联设备，以便通过Siri语音控制。

- **插件**

> 1. homebridge-better-http-rgb ：通过 http/https 控制灯。

#### 壹：方案框架
- 物理层次
![-w1162](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/物理层次.jpg)
- 数据链路
![-w1066](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/数据链路.jpg)

#### 贰：技术实现
##### 第一步：安装并启动 HomeBridge 服务
- 1. 启动树莓派，通过有线网络连接电脑和树莓派，配置Wi-Fi。参考[树莓派装载系统并配置网络](https://www.jianshu.com/p/dc4da0330b2a)
- 2. 安装 HomeBridge。参考[HomeBridge在树莓派上的安装](https://github.com/homebridge/homebridge/wiki/Install-Homebridge-on-Raspbian)
- 3. 安装 homebridge-better-http-rgb。参考[此链接](https://www.npmjs.com/package/homebridge-better-http-rgb)，注意命令前面添加 **`sudo`**。
- 4. 配置（模拟）需要控制的设备。

>
   ``` 
    cd ~/.homebridge
    vim config.json 
    ```
添加下面内容

```json

{
    "bridge": {
        "name": "Homebridge",
        "username": "DC:A6:32:64:5B:41",
        "port": 51826,
        "pin": "888-88-888"
    },
    "description": "Homebridge",
    "accessories": [
        {
            "accessory": "HTTP-RGB",
            "name": "灯1",
            "service": "Light",
	    "http_method": "POST",
            "switch": {
                "status": "http://localhost:8006/light/api/v1.0/d896e0004500001b/1/",
                "powerOn": "http://localhost:8006/light/api/v1.0/d896e0004500001b/1/on",
                "powerOff": "http://localhost:8006/light/api/v1.0/d896e0004500001b/1/off"
            }
        }
    ],
    "platforms": []
}
```

- 1. 开机启动 HomeBridge。

> 
 ```
   cd /etc/systemd/system
   vim homebridge@pi.service
 ```
 添加下面内容。

```
[Unit]
Description=Homebridge
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/homebridge

[Install]
WantedBy=multi-user.target
```

> 常用命令
 
```
#更新系统服务设置
sudo systemctl --system daemon-reload 

#设置 HomeBridge 开机启动
sudo systemctl enable homebridge@pi.service 

#常用操作
sudo systemctl stop homebridge@pi.service
sudo systemctl status homebridge@pi.service 
journalctl -f -n 50  -u homebridge@pi.service 
```

##### 第二步：构建逻辑控制 HTTP 服务
- 1. 安装 Flask 。`pip3 install flask` 
- 2. 安装 tencentcloud-sdk-python 。`pip3 install tencentcloud-sdk-python`
- 3. 编写逻辑控制服务。

> 
```sh 
   cd ~/
   mkdir tencent_iot_explorer
   cd tencent_iot_explorer
   vim app_tencent_iot_demo.py
```
添加下面内容。

```python
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
```

- 1. 开机启动 app_tencent_iot_demo.py。

> `cd /etc/systemd/system`

> `vim fmtech@pi.service` 
> 添加下面内容。

```
[Unit]
Description=fmtech-iot-demo
After=network.target

[Service]
Type=simple
User=pi
ExecStart=python3 /home/pi/tencent_iot_explorer/app_tencent_iot_demo.py

[Install]
WantedBy=multi-user.target
```

> 常用命令

```
#更新系统服务设置
sudo systemctl --system daemon-reload

#设置 fmtech 开机启动
sudo systemctl enable fmtech@pi.service

#常用操作
sudo systemctl stop fmtech@pi.service
sudo systemctl status fmtech@pi.service 
journalctl -f -n 50  -u fmtech@pi.service
```

##### 第三步：IotExplore 添加产品及解析脚本
- 1. 登陆腾讯云并前往[物联网开发平台](https://console.cloud.tencent.com/iotexplorer)
- 2. 创建项目。
![-w1104](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/创建项目.jpg)
- 3. 创建产品。
![-w1229](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/创建产品.jpg)
- 4. 点击创建的产品，添加产品属性。
![-w991](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/led_switch属性.jpg)
![-w932](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/heartbeart_periods属性.jpg)

- 5. 更新设备类型为 Class C。
![-w958](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/img/修改ClssC.jpg)
- 1. 确定应用层[通信协议](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/code/iot-explorer/通信协议.md)，添加数据解析脚本。
    
```js
//上行，设备上报数据
function RawToProtocol(fPort, bytes) {
	var COMMAND_STATE_REPORT = 0x00;
    var COMMAND_CONFIG_REPORT = 0x02;

    var COMMAND_STATE_GET = 0x80;
    var COMMAND_CONFIG_GET = 0x81;

    var COMMAND_HEARTBEAT_SET = 0x82;
    var COMMAND_LED_STATE_SET = 0x84;
 

    var data = {
        "method": "report",
        "clientToken": new Date(),
        "params": {}
    };


    var cmd = bytes[0]; // command
    var porocol_ver = bytes[1]; // 协议版本

    if (cmd === COMMAND_STATE_REPORT) {
        data.params.led_switch = bytes[2] & 0x01;
        return data;
    }
    
      if (cmd === COMMAND_STATE_REPORT) {
        data.params.heartbeat_period = bytes[2];
        return data;
    }

    return data;
}

// 下行，服务端下发数据

function ProtocolToRaw(obj) {
    var COMMAND_STATE_REPORT = 0x00;
    var COMMAND_CONFIG_REPORT = 0x02;

    var COMMAND_STATE_GET = 0x80;
    var COMMAND_CONFIG_GET = 0x81;

    var COMMAND_HEARTBEAT_SET = 0x82;
    var COMMAND_LED_STATE_SET = 0x84;


   var payloadArray = []
  // 追加下行帧头部
    payloadArray = payloadArray.concat(0x0a); // 设备短应用程序端口
    payloadArray = payloadArray.concat(0x01); // LoRa数据包类型，1 confirm包，0 非confirm包
    var params = obj['params'];

    if (params.hasOwnProperty('heartbeat_period')) {

        var heartbeat_period = params['heartbeat_period'];
        payloadArray = payloadArray.concat(COMMAND_HEARTBEAT_SET);
        payloadArray = payloadArray.concat(0x01);
        payloadArray = payloadArray.concat(heartbeat_period);
        return payloadArray;
    }

    if (params.hasOwnProperty('led_switch')) {
        var state = params['led_switch'];
        payloadArray = payloadArray.concat(COMMAND_LED_STATE_SET);
        payloadArray = payloadArray.concat(0x01);
        payloadArray = payloadArray.concat(state);
        return payloadArray;
    }

    return payloadArray;
}
```
- 7. 根据需要进行设备调试。

##### 第四步：终端节点开发
- 搭建开发环境。请参考腾讯云Iot部门给出的[参考文档](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/code/iot-explorer/基于TencentOS%20tiny的LoRaWAN开发入门指南.pdf)。
- 根据[协议](https://github.com/hutao-fmtech/tencent-iot-contest-demo/blob/master/code/iot-explorer/通信协议.md)编码。建议使用Tencent-TinyOS，后期更换硬件平台更方便。

##### 第五步：集成测试
- 硬件准备。

> 1. LoRaWAN 网关上电并连接互联网。
> 2. 确认节点已经接入腾讯云IotExplorer。
> 3. 确认树莓派和iPone 手机接入同一WiFi。

- 测试体验。

#### 叁：总结 & 拓展
方案本身无特别的自创技术，都是在站在巨人的肩膀上开始集成。本方案的技术框架，只能作为DIY使用，在真正的产品中，工程的复杂度还是偏高，需要使用类似边缘计算的方式来架构产品，形成 **【端--云--边】** 的产品结构，才能正在的市场化。

##### 3.1 方案要点：
- 充分利用 Apple 的智能家居技术能力， 通过 Siri 获取目标设备与执行动作。
- LoRaWAN 网络服务器使用腾讯云提供的Iot Explore，利用平台能力，降低集成复杂度。
- 使用 HomeBridge 桥接客制化设备，遇到复杂控制终端，可编写插件，自由扩展。

##### 3.2 运用拓展：
- 更多的控制终端，控制场景更加丰富：窗帘、空调、门禁等。
- 更多的输入终端，场景自动化： 温湿度传感器、亮度传感器、空间占用传感器。
- 更多的逻辑控制单元，运营自动化：设备状态实时看板、运维监控。

#### 肆：致谢 
感谢腾讯云IoT创新大赛组委会为大家提供的开发套件及技术支持，并为大家准备了一个交流平台。



