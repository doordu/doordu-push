import logging

import paho.mqtt.publish as publish


class MQTT:
    def __init__(self, host, port=1883):
        self.host = host
        self.port = port

    def push(self, topic, qos, message):
        logging.info("开始MQTT推送")
        logging.info("topic: %s", topic)
        logging.info("QOS: %d", qos)
        try:
            publish.single(topic, message, qos=qos, hostname=self.host,
                           port=self.port)
        except Exception:
            logging.error("MQTT推送失败")
        logging.info("MQTT推送结束")
        return {'mqtt': None}
