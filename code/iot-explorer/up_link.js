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
        data.params.led_state = bytes[2] & 0x01;
        return data;
    }

      if (cmd === COMMAND_STATE_REPORT) {
        data.params.heartbeat_period = bytes[2];
        return data;
    }

    return data;
}

