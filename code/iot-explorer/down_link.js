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

    if (params.hasOwnProperty('led_state')) {
        var state = params['led_state'];
        payloadArray = payloadArray.concat(COMMAND_LED_STATE_SET);
        payloadArray = payloadArray.concat(0x01);
        payloadArray = payloadArray.concat(state);
        return payloadArray;
    }

    return payloadArray;
}
