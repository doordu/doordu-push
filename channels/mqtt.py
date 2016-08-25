import paho.mqtt.publish as publish


class MQTT:
    def __init__(self, logger, host, port=1883):
        self.logger = logger
        self.host = host
        self.port = port

    def push(self, topic, qos, message):
        self.logger.info("开始MQTT推送")
        self.logger.info("topic: %s", topic)
        self.logger.info("QOS: %d", qos)
        publish.single(topic, message, qos=qos, hostname=self.host,
                       port=self.port)
        self.logger.info("MQTT推送结束")
        return {'mqtt': None}
